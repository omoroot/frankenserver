var g=document,k=Array,m=Error,aa=parseInt,n=String;function p(a,b){return a.keyCode=b}function q(a,b){return a.currentTarget=b}function r(a,b){return a.disabled=b}
var s="shift",t="replace",u="preventDefault",v="keyCode",w="toString",x="propertyIsEnumerable",ba="checked",y="split",z="style",A="push",B="slice",C="value",D="indexOf",E="type",ca="name",F="length",G="prototype",da="target",H="call",I,J=this,K=function(a){var b=typeof a;if("object"==b)if(a){if(a instanceof k)return"array";if(a instanceof Object)return b;var c=Object[G][w][H](a);if("[object Window]"==c)return"object";if("[object Array]"==c||"number"==typeof a[F]&&"undefined"!=typeof a.splice&&"undefined"!=
typeof a[x]&&!a[x]("splice"))return"array";if("[object Function]"==c||"undefined"!=typeof a[H]&&"undefined"!=typeof a[x]&&!a[x]("call"))return"function"}else return"null";else if("function"==b&&"undefined"==typeof a[H])return"object";return b},ea=function(a){var b=K(a);return"array"==b||"object"==b&&"number"==typeof a[F]},L=function(a){return"string"==typeof a},fa=function(a){var b=typeof a;return"object"==b&&null!=a||"function"==b},ga=function(a,b){function c(){}c.prototype=b[G];a.t=b[G];a.prototype=
new c;a.A=function(a,c,e){return b[G][c].apply(a,k[G][B][H](arguments,2))}};var M=function(a){if(m.captureStackTrace)m.captureStackTrace(this,M);else{var b=m().stack;b&&(this.stack=b)}a&&(this.message=n(a))};ga(M,m);M[G].name="CustomError";var ha=function(a,b){for(var c=a[y]("%s"),d="",f=k[G][B][H](arguments,1);f[F]&&1<c[F];)d+=c[s]()+f[s]();return d+c.join("%s")},ia=n[G].trim?function(a){return a.trim()}:function(a){return a[t](/^[\s\xa0]+|[\s\xa0]+$/g,"")},qa=function(a,b){if(b)a=a[t](ja,"&amp;")[t](ka,"&lt;")[t](la,"&gt;")[t](ma,"&quot;")[t](na,"&#39;")[t](oa,"&#0;");else{if(!pa.test(a))return a;-1!=a[D]("&")&&(a=a[t](ja,"&amp;"));-1!=a[D]("<")&&(a=a[t](ka,"&lt;"));-1!=a[D](">")&&(a=a[t](la,"&gt;"));-1!=a[D]('"')&&(a=a[t](ma,"&quot;"));
-1!=a[D]("'")&&(a=a[t](na,"&#39;"));-1!=a[D]("\x00")&&(a=a[t](oa,"&#0;"))}return a},ja=/&/g,ka=/</g,la=/>/g,ma=/"/g,na=/'/g,oa=/\x00/g,pa=/[\x00&<>"']/,ra=function(a,b){return a<b?-1:a>b?1:0},sa=function(a){return n(a)[t](/\-([a-z])/g,function(a,c){return c.toUpperCase()})},ta=function(a,b){var c=L(b)?n(b)[t](/([-()\[\]{}+?*.$\^|,:#<!\\])/g,"\\$1")[t](/\x08/g,"\\x08"):"\\s";return a[t](new RegExp("(^"+(c?"|["+c+"]+":"")+")([a-z])","g"),function(a,b,c){return b+c.toUpperCase()})};var ua=function(a,b){b.unshift(a);M[H](this,ha.apply(null,b));b[s]()};ga(ua,M);ua[G].name="AssertionError";var N=function(a,b,c){if(!a){var d="Assertion failed";if(b)var d=d+(": "+b),f=k[G][B][H](arguments,2);throw new ua(""+d,f||[]);}return a};var O=k[G],va=O[D]?function(a,b,c){N(null!=a[F]);return O[D][H](a,b,c)}:function(a,b,c){c=null==c?0:0>c?Math.max(0,a[F]+c):c;if(L(a))return L(b)&&1==b[F]?a[D](b,c):-1;for(;c<a[F];c++)if(c in a&&a[c]===b)return c;return-1},wa=O.forEach?function(a,b,c){N(null!=a[F]);O.forEach[H](a,b,c)}:function(a,b,c){for(var d=a[F],f=L(a)?a[y](""):a,e=0;e<d;e++)e in f&&b[H](c,f[e],e,a)},xa=function(a){var b=a[F];if(0<b){for(var c=k(b),d=0;d<b;d++)c[d]=a[d];return c}return[]};var ya=function(a,b,c){for(var d in a)b[H](c,a[d],d,a)},za="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" "),Aa=function(a,b){for(var c,d,f=1;f<arguments[F];f++){d=arguments[f];for(c in d)a[c]=d[c];for(var e=0;e<za[F];e++)c=za[e],Object[G].hasOwnProperty[H](d,c)&&(a[c]=d[c])}};var P;t:{var Ba=J.navigator;if(Ba){var Ca=Ba.userAgent;if(Ca){P=Ca;break t}}P=""};var Da=-1!=P[D]("Opera")||-1!=P[D]("OPR"),Q=-1!=P[D]("Trident")||-1!=P[D]("MSIE"),R=-1!=P[D]("Gecko")&&-1==P.toLowerCase()[D]("webkit")&&!(-1!=P[D]("Trident")||-1!=P[D]("MSIE")),S=-1!=P.toLowerCase()[D]("webkit"),Ea=function(){var a=J.document;return a?a.documentMode:void 0},Fa=function(){var a="",b;if(Da&&J.opera)return a=J.opera.version,"function"==K(a)?a():a;R?b=/rv\:([^\);]+)(\)|;)/:Q?b=/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/:S&&(b=/WebKit\/(\S+)/);b&&(a=(a=b.exec(P))?a[1]:"");return Q&&(b=Ea(),b>
parseFloat(a))?n(b):a}(),Ga={},T=function(a){var b;if(!(b=Ga[a])){b=0;for(var c=ia(n(Fa))[y]("."),d=ia(n(a))[y]("."),f=Math.max(c[F],d[F]),e=0;0==b&&e<f;e++){var h=c[e]||"",l=d[e]||"",cb=RegExp("(\\d*)(\\D*)","g"),db=RegExp("(\\d*)(\\D*)","g");do{var U=cb.exec(h)||["","",""],V=db.exec(l)||["","",""];if(0==U[0][F]&&0==V[0][F])break;b=ra(0==U[1][F]?0:aa(U[1],10),0==V[1][F]?0:aa(V[1],10))||ra(0==U[2][F],0==V[2][F])||ra(U[2],V[2])}while(0==b)}b=Ga[a]=0<=b}return b},Ha=J.document,Ia=Ha&&Q?Ea()||("CSS1Compat"==
Ha.compatMode?aa(Fa,10):5):void 0;var Ja=!Q||Q&&9<=Ia;!R&&!Q||Q&&Q&&9<=Ia||R&&T("1.9.1");Q&&T("9");var W=function(a,b){return L(b)?a.getElementById(b):b},Ka=function(a,b,c,d){a=d||a;var f=b&&"*"!=b?b.toUpperCase():"";if(a.querySelectorAll&&a.querySelector&&(f||c))return a.querySelectorAll(f+(c?"."+c:""));if(c&&a.getElementsByClassName){b=a.getElementsByClassName(c);if(f){a={};for(var e=d=0,h;h=b[e];e++)f==h.nodeName&&(a[d++]=h);a.length=d;return a}return b}b=a.getElementsByTagName(f||"*");if(c){a={};for(e=d=0;h=b[e];e++){var f=h.className,l;if(l="function"==typeof f[y])l=0<=va(f[y](/\s+/),c);l&&
(a[d++]=h)}a.length=d;return a}return b},Ma=function(a,b){ya(b,function(b,d){"style"==d?a[z].cssText=b:"class"==d?a.className=b:"for"==d?a.htmlFor=b:d in La?a.setAttribute(La[d],b):0==d.lastIndexOf("aria-",0)||0==d.lastIndexOf("data-",0)?a.setAttribute(d,b):a[d]=b})},La={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",role:"role",rowspan:"rowSpan",type:"type",usemap:"useMap",valign:"vAlign",width:"width"},Oa=function(a,
b,c){var d=arguments,f=d[0],e=d[1];if(!Ja&&e&&(e[ca]||e[E])){f=["<",f];e[ca]&&f[A](' name="',qa(e[ca]),'"');if(e[E]){f[A](' type="',qa(e[E]),'"');var h={};Aa(h,e);delete h[E];e=h}f[A](">");f=f.join("")}f=g.createElement(f);e&&(L(e)?f.className=e:"array"==K(e)?f.className=e.join(" "):Ma(f,e));2<d[F]&&Na(g,f,d,2);return f},Na=function(a,b,c,d){function f(c){c&&b.appendChild(L(c)?a.createTextNode(c):c)}for(;d<c[F];d++){var e=c[d];if(!ea(e)||fa(e)&&0<e.nodeType)f(e);else{var h;t:{if(e&&"number"==typeof e[F]){if(fa(e)){h=
"function"==typeof e.item||"string"==typeof e.item;break t}if("function"==K(e)){h="function"==typeof e.item;break t}}h=!1}wa(h?xa(e):e,f)}}};var Pa=function(a){var b=a[E];if(void 0===b)return null;switch(b.toLowerCase()){case "checkbox":case "radio":return a[ba]?a[C]:null;case "select-one":return b=a.selectedIndex,0<=b?a.options[b][C]:null;case "select-multiple":for(var b=[],c,d=0;c=a.options[d];d++)c.selected&&b[A](c[C]);return b[F]?b:null;default:return void 0!==a[C]?a[C]:null}};var Qa=function(a){Qa[" "](a);return a};Qa[" "]=function(){};var Ra=!Q||Q&&9<=Ia,Sa=Q&&!T("9");!S||T("528");R&&T("1.9b")||Q&&T("8")||Da&&T("9.5")||S&&T("528");R&&!T("8")||Q&&T("9");var Ta=function(a,b){this.type=a;this.target=b;q(this,this[da]);this.defaultPrevented=this.o=!1};Ta[G].preventDefault=function(){this.defaultPrevented=!0};R&&T(17);var X=function(a,b){Ta[H](this,a?a[E]:"");this.target=null;q(this,null);this.relatedTarget=null;this.button=this.screenY=this.screenX=this.clientY=this.clientX=this.offsetY=this.offsetX=0;p(this,0);this.charCode=0;this.metaKey=this.shiftKey=this.altKey=this.ctrlKey=!1;this.p=this.state=null;a&&this.u(a,b)};ga(X,Ta);
X[G].u=function(a,b){var c=this.type=a[E];this.target=a[da]||a.srcElement;q(this,b);var d=a.relatedTarget;if(d){if(R){var f;t:{try{Qa(d.nodeName);f=!0;break t}catch(e){}f=!1}f||(d=null)}}else"mouseover"==c?d=a.fromElement:"mouseout"==c&&(d=a.toElement);this.relatedTarget=d;this.offsetX=S||void 0!==a.offsetX?a.offsetX:a.layerX;this.offsetY=S||void 0!==a.offsetY?a.offsetY:a.layerY;this.clientX=void 0!==a.clientX?a.clientX:a.pageX;this.clientY=void 0!==a.clientY?a.clientY:a.pageY;this.screenX=a.screenX||
0;this.screenY=a.screenY||0;this.button=a.button;p(this,a[v]||0);this.charCode=a.charCode||("keypress"==c?a[v]:0);this.ctrlKey=a.ctrlKey;this.altKey=a.altKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey;this.state=a.state;this.p=a;a.defaultPrevented&&this[u]()};X[G].preventDefault=function(){X.t[u][H](this);var a=this.p;if(a[u])a[u]();else if(a.returnValue=!1,Sa)try{(a.ctrlKey||112<=a[v]&&123>=a[v])&&p(a,-1)}catch(b){}};var Ua="closure_listenable_"+(1E6*Math.random()|0),Va=0;var Wa=function(a,b,c,d,f,e){this.c=a;this.g=b;this.src=c;this.type=d;this.k=!!f;this.j=e;this.key=++Va;this.e=this.l=!1};Wa[G].n=function(){this.e=!0;this.j=this.src=this.g=this.c=null};var Xa=function(a){this.src=a;this.a={};this.m=0};Xa[G].add=function(a,b,c,d,f){var e=a[w]();a=this.a[e];a||(a=this.a[e]=[],this.m++);var h;t:{for(h=0;h<a[F];++h){var l=a[h];if(!l.e&&l.c==b&&l.k==!!d&&l.j==f)break t}h=-1}-1<h?(b=a[h],c||(b.l=!1)):(b=new Wa(b,null,this.src,e,!!d,f),b.l=c,a[A](b));return b};Xa[G].q=function(a){var b=a[E];if(!(b in this.a))return!1;var c=this.a[b],d=va(c,a),f;if(f=0<=d)N(null!=c[F]),O.splice[H](c,d,1);f&&(a.n(),0==this.a[b][F]&&(delete this.a[b],this.m--));return f};var Ya="closure_lm_"+(1E6*Math.random()|0),Za={},$a=0,ab=function(a,b,c,d,f){if("array"==K(b)){for(var e=0;e<b[F];e++)ab(a,b[e],c,d,f);return null}c=bb(c);if(a&&a[Ua])a=a.w(b,c,d,f);else{if(!b)throw m("Invalid event type");var e=!!d,h=eb(a);h||(a[Ya]=h=new Xa(a));c=h.add(b,c,!1,d,f);c.g||(d=fb(),c.g=d,d.src=a,d.c=c,a.addEventListener?a.addEventListener(b[w](),d,e):a.attachEvent(gb(b[w]()),d),$a++);a=c}return a},fb=function(){var a=hb,b=Ra?function(c){return a[H](b.src,b.c,c)}:function(c){c=a[H](b.src,
b.c,c);if(!c)return c};return b},gb=function(a){return a in Za?Za[a]:Za[a]="on"+a},jb=function(a,b,c,d){var f=1;if(a=eb(a))if(b=a.a[b[w]()])for(b=b.concat(),a=0;a<b[F];a++){var e=b[a];e&&e.k==c&&!e.e&&(f&=!1!==ib(e,d))}return Boolean(f)},ib=function(a,b){var c=a.c,d=a.j||a.src;if(a.l&&"number"!=typeof a&&a&&!a.e){var f=a.src;if(f&&f[Ua])f.v(a);else{var e=a[E],h=a.g;f.removeEventListener?f.removeEventListener(e,h,a.k):f.detachEvent&&f.detachEvent(gb(e),h);$a--;(e=eb(f))?(e.q(a),0==e.m&&(e.src=null,
f[Ya]=null)):a.n()}}return c[H](d,b)},hb=function(a,b){if(a.e)return!0;if(!Ra){var c;if(!(c=b))t:{c=["window","event"];for(var d=J,f;f=c[s]();)if(null!=d[f])d=d[f];else{c=null;break t}c=d}f=c;c=new X(f,this);d=!0;if(!(0>f[v]||void 0!=f.returnValue)){t:{var e=!1;if(0==f[v])try{p(f,-1);break t}catch(h){e=!0}if(e||void 0==f.returnValue)f.returnValue=!0}f=[];for(e=c.currentTarget;e;e=e.parentNode)f[A](e);for(var e=a[E],l=f[F]-1;!c.o&&0<=l;l--)q(c,f[l]),d&=jb(f[l],e,!0,c);for(l=0;!c.o&&l<f[F];l++)q(c,
f[l]),d&=jb(f[l],e,!1,c)}return d}return ib(a,new X(b,this))},eb=function(a){a=a[Ya];return a instanceof Xa?a:null},kb="__closure_events_fn_"+(1E9*Math.random()>>>0),bb=function(a){N(a,"Listener can not be null.");if("function"==K(a))return a;N(a.handleEvent,"An object listener must have handleEvent method.");a[kb]||(a[kb]=function(b){return a.handleEvent(b)});return a[kb]};var lb=function(a,b,c){t:if(c=sa(c),void 0===a[z][c]){var d=(S?"Webkit":R?"Moz":Q?"ms":Da?"O":null)+ta(c);if(void 0!==a[z][d]){c=d;break t}}c&&(a[z][c]=b)};var mb=function(a,b){var c=[];1<arguments[F]&&(c=k[G][B][H](arguments)[B](1));var d=Ka(g,"th","tct-selectall",a);if(0!=d[F]){var d=d[0],f=0,e=Ka(g,"tbody",null,a);e[F]&&(f=e[0].rows[F]);this.d=Oa("input",{type:"checkbox"});d.appendChild(this.d);f?ab(this.d,"click",this.s,!1,this):r(this.d,!0);this.f=[];this.h=[];this.i=[];d=Ka(g,"input",null,a);for(f=0;e=d[f];f++)"checkbox"==e[E]&&e!=this.d?(this.f[A](e),ab(e,"click",this.r,!1,this)):"action"==e[ca]&&(0<=c[D](e[C])?this.i[A](e):this.h[A](e),r(e,!0))}};
I=mb[G];I.f=null;I.b=0;I.d=null;I.h=null;I.i=null;I.s=function(a){for(var b=a[da][ba],c=a=0,d;d=this.f[c];c++)d.checked=b,a+=1;this.b=b?this.f[F]:0;for(c=0;b=this.h[c];c++)r(b,!this.b);for(c=0;b=this.i[c];c++)r(b,1!=a?!0:!1)};I.r=function(a){this.b+=a[da][ba]?1:-1;this.d.checked=this.b==this.f[F];a=0;for(var b;b=this.h[a];a++)r(b,!this.b);for(a=0;b=this.i[a];a++)r(b,1!=this.b?!0:!1)};var nb=function(){var a=W(g,"kinds");a&&new mb(a);(a=W(g,"pending_backups"))&&new mb(a);(a=W(g,"backups"))&&new mb(a,"Restore");var b=W(g,"ae-datastore-admin-filesystem");b&&ab(b,"change",function(){var a="gs"==Pa(b);W(g,"gs_bucket_tr")[z].display=a?"":"none"});if(a=W(g,"confirm_delete_form")){var c=W(g,"confirm_readonly_delete");c&&(a.onsubmit=function(){var a=W(g,"confirm_message");if(L("color"))lb(a,"red","color");else for(var b in"color")lb(a,"color"[b],b);return c[ba]})}},Y=["ae","Datastore",
"Admin","init"],Z=J;Y[0]in Z||!Z.execScript||Z.execScript("var "+Y[0]);for(var $;Y[F]&&($=Y[s]());)Y[F]||void 0===nb?Z=Z[$]?Z[$]:Z[$]={}:Z[$]=nb;
