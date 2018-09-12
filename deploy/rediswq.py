import redis
import uuid
import hashlib


class RedisWQ:
    """
    Based on:
    https://kubernetes.io/docs/tasks/job/fine-parallel-processing-work-queue/
    Simple Finite Work Queue with Redis Backend
    This work queue is finite: as long as no more work is added
    after workers start, the workers can detect when the queue
    is completely empty.
    The items in the work queue are assumed to have unique values.
    This object is not intended to be used by multiple threads
    concurrently.
    """
    def __init__(self, name, **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0
        The work queue is identified by "name".  The library may create other
        keys with "name" as a prefix.
        """
        self._db = redis.StrictRedis(**redis_kwargs)
        # The session ID will uniquely identify this "worker".
        self._session = str(uuid.uuid4())
        # Work queue is implemented as two queues: main, and processing.
        # Work is initially in main, and moved to processing when a client
        # picks it up.
        self._main_q_key = name
        self._processing_q_key = name + ":processing"
        self._lease_key_prefix = name + ":leased_by_session:"

    def sessionID(self):
        """Return the ID for this session."""
        return self._session

    def _main_qsize(self):
        """Return the size of the main queue."""
        return self._db.llen(self._main_q_key)

    def _processing_qsize(self):
        """Return the size of the main queue."""
        return self._db.llen(self._processing_q_key)

    def empty(self):
        """Return True if the queue is empty, including work being done,
        False otherwise. False does not necessarily mean that there is work
        available to work on right now.
        """
        return self._main_qsize() == 0 and self._processing_qsize() == 0

    def _itemkey(self, item):
        """Returns a string that uniquely identifies an item (bytes)."""
        return hashlib.sha224(item).hexdigest()

    def _lease_exists(self, item):
        """True if a lease on 'item' exists."""
        return self._db.exists(self._lease_key_prefix + self._itemkey(item))

    def put(self, item):
        """Put item into the queue."""
        self._db.rpush(self._main_q_key, item)

    def lease(self, lease_secs=600, block=True, timeout=None):
        """Begin working on an item the work queue.
        Lease the item for lease_secs.  After that time, other
        workers may consider this client to have crashed or stalled
        and pick up the item instead.
        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self._db.brpoplpush(
                self._main_q_key, self._processing_q_key, timeout=timeout
            )
        else:
            item = self._db.rpoplpush(self._main_q_key, self._processing_q_key)
        if item:
            # Record that we (this session id) are working on a key. Expire
            # that note after the lease timeout.
            # Note: if we crash at this line of the program, then GC will
            # see no lease for this item a later return it to the main queue.
            itemkey = self._itemkey(item)
            self._db.setex(
                self._lease_key_prefix + itemkey, lease_secs, self._session
            )
        return item

    def complete(self, value):
        """Complete working on the item with 'value'.
        If the lease expired, the item may not have completed, and some
        other worker may have picked it up.  There is no indication
        of what happened.
        """
        self._db.lrem(self._processing_q_key, 0, value)
        # If we crash here, then the GC code will try to move the value,
        # but it will not be here, which is fine.  So this does not need
        # to be a transaction.
        itemkey = self._itemkey(value)
        self._db.delete(self._lease_key_prefix + itemkey, self._session)
