import betamax
from betamax_serializers import pretty_json

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
