/*
 * jQuery resize event - v1.1 - 3/14/2010
 * http://benalman.com/projects/jquery-resize-plugin/
 * 
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
!function(t,i,e){"$:nomunge";function n(){h=i[o](function(){r.each(function(){var i=t(this),e=i.width(),n=i.height(),h=t.data(this,d);e===h.w&&n===h.h||i.trigger(s,[h.w=e,h.h=n])}),n()},a[u])}var h,r=t([]),a=t.resize=t.extend(t.resize,{}),o="setTimeout",s="resize",d=s+"-special-event",u="delay";a[u]=250,a.throttleWindow=!0,t.event.special[s]={setup:function(){if(!a.throttleWindow&&this[o])return!1;var i=t(this);r=r.add(i),t.data(this,d,{w:i.width(),h:i.height()}),1===r.length&&n()},teardown:function(){if(!a.throttleWindow&&this[o])return!1;var i=t(this);r=r.not(i),i.removeData(d),r.length||clearTimeout(h)},add:function(i){function n(i,n,r){var a=t(this),o=t.data(this,d);o||(o=t.data(this,d,{})),o.w=n!==e?n:a.width(),o.h=r!==e?r:a.height(),h.apply(this,arguments)}if(!a.throttleWindow&&this[o])return!1;var h;if(t.isFunction(i))return h=i,n;h=i.handler,i.handler=n}}}(jQuery,this);