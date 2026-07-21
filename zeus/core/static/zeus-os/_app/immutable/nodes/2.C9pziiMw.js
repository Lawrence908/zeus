const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["_app/immutable/assets/xterm.CFbL2ovg.css","_app/immutable/chunks/V3Cqym1g.js","_app/immutable/chunks/BdTEKTSI.js","_app/immutable/chunks/S5t-rHtA.js","_app/immutable/chunks/DLTTJqzu.js","_app/immutable/assets/editor.BwRAHMTc.css"])))=>i.map(i=>d[i]);
var Jp=Object.defineProperty;var Qp=(n,e,t)=>e in n?Jp(n,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):n[e]=t;var Dt=(n,e,t)=>Qp(n,typeof e!="symbol"?e+"":e,t);import{b as To,a as j,f as ie,t as ea,c as Ai}from"../chunks/D0yluyF4.js";import"../chunks/B2o7WAYw.js";import{w as _i,d as ja,g as qn,a as zt,o as Jt,c as jp}from"../chunks/DLTTJqzu.js";import{aq as tn,ao as Ks,aD as em,X as Hf,a3 as wo,b6 as Ba,ak as Jr,ah as s,aU as tm,o as nm,bb as Du,b7 as Ao,ap as jr,d as Gf,H as im,av as ku,a4 as Ti,j as li,Y as bl,ab as rm,b9 as am,a9 as tr,az as Vf,W as yc,i as sm,h as om,aK as ue,bc as Uu,E as lm,D as cm,aZ as Wf,aO as $f,I as Ro,b as um,_ as dm,aJ as fm,aa as hm,al as Xf,g as qf,aT as Ec,f as pm,bh as me,Q as Yf,aV as mm,as as gm,m as _m,a2 as vm,t as xm,s as bm,l as Sm,B as ym,R as Em,ac as Kf,K as Mm,aC as Tm,aN as xa,bo as Zf,bk as L,M as wm,O as Am,C as Ou,y as Fu,aH as Jf,b1 as Rm,ay as Cm,bg as Im,F as Nm,V as Pm,r as Lm,A as Dm,N as km,q as Um,am as Om,aj as Fm,bi as vr,aX as Bm,a0 as zm,bn as Hm,bm as Bu,a$ as zu,a_ as Gm,a5 as tt,a8 as Vm,aS as Mt,aF as lt,aG as Ht,b2 as W,aP as Tt,$ as Qf,Z as M,ba as U,aY as S,aW as fo,af as Pt,aL as Hn,bl as nr,aM as kn,aw as Nr,bj as jf}from"../chunks/S5t-rHtA.js";import{B as Wm,_ as Pa,p as ft,b as Er,i as Ae,c as Mc,a as un,s as ua}from"../chunks/BdTEKTSI.js";import{a as $m,e as Re,s as ee}from"../chunks/D0n4Inod.js";const Xm=Symbol("NaN");function qm(n,e,t){tn&&Ks();var i=new Wm(n),r=!em();Hf(()=>{var a=e();a!==a&&(a=Xm),r&&a!==null&&typeof a=="object"&&(a={}),i.ensure(a,t)})}function $n(n,e){return e}function Ym(n,e,t){for(var i=[],r=e.length,a,o=e.length,l=0;l<r;l++){let h=e[l];$f(h,()=>{if(a){if(a.pending.delete(h),a.done.add(h),a.pending.size===0){var d=n.outrogroups;Sl(n,yc(a.done)),d.delete(a),d.size===0&&(n.outrogroups=null)}}else o-=1},!1)}if(o===0){var c=i.length===0&&t!==null;if(c){var u=t,f=u.parentNode;dm(f),f.append(u),n.items.clear()}Sl(n,e,!c)}else a={pending:new Set(e),done:new Set},(n.outrogroups??(n.outrogroups=new Set)).add(a)}function Sl(n,e,t=!0){var i;if(n.pending.size>0){i=new Set;for(const o of n.pending.values())for(const l of o)i.add(n.items.get(l).e)}for(var r=0;r<e.length;r++){var a=e[r];if(i!=null&&i.has(a)){a.f|=li;const o=document.createDocumentFragment();fm(a,o)}else hm(e[r],t)}}var Hu;function ct(n,e,t,i,r,a=null){var o=n,l=new Map,c=(e&qf)!==0;if(c){var u=n;o=tn?Ba(Jr(u)):u.appendChild(wo())}tn&&Ks();var f=null,h=tr(()=>{var D=t();return Vf(D)?D:D==null?[]:yc(D)}),d,p=new Map,m=!0;function E(D){O.effect.f&cm||(O.pending.delete(D),O.fallback=f,Km(O,d,o,e,i),f!==null&&(d.length===0?f.f&li?(f.f^=li,La(f,null,o)):Wf(f):$f(f,()=>{f=null})))}function g(D){O.pending.delete(D)}var _=Hf(()=>{d=s(h);var D=d.length;let y=!1;if(tn){var B=tm(o)===nm;B!==(D===0)&&(o=Du(),Ba(o),Ao(!1),y=!0)}for(var R=new Set,C=Ti,b=am(),A=0;A<D;A+=1){tn&&jr.nodeType===Gf&&jr.data===im&&(o=jr,y=!0,Ao(!1));var k=d[A],z=i(k,A),H=m?null:l.get(z);H?(H.v&&ku(H.v,k),H.i&&ku(H.i,A),b&&C.unskip_effect(H.e)):(H=Zm(l,m?o:Hu??(Hu=wo()),k,z,A,r,e,t),m||(H.e.f|=li),l.set(z,H)),R.add(z)}if(D===0&&a&&!f&&(m?f=bl(()=>a(o)):(f=bl(()=>a(Hu??(Hu=wo()))),f.f|=li)),D>R.size&&rm(),tn&&D>0&&Ba(Du()),!m)if(p.set(C,R),b){for(const[q,Q]of l)R.has(q)||C.skip_effect(Q.e);C.oncommit(E),C.ondiscard(g)}else E(C);y&&Ao(!0),s(h)}),O={effect:_,items:l,pending:p,outrogroups:null,fallback:f};m=!1,tn&&(o=jr)}function ba(n){for(;n!==null&&!(n.f&um);)n=n.next;return n}function Km(n,e,t,i,r){var k,z,H,q,Q,G,T,w,I;var a=(i&pm)!==0,o=e.length,l=n.items,c=ba(n.effect.first),u,f=null,h,d=[],p=[],m,E,g,_;if(a)for(_=0;_<o;_+=1)m=e[_],E=r(m,_),g=l.get(E).e,g.f&li||((z=(k=g.nodes)==null?void 0:k.a)==null||z.measure(),(h??(h=new Set)).add(g));for(_=0;_<o;_+=1){if(m=e[_],E=r(m,_),g=l.get(E).e,n.outrogroups!==null)for(const F of n.outrogroups)F.pending.delete(g),F.done.delete(g);if(g.f&Ro&&(Wf(g),a&&((q=(H=g.nodes)==null?void 0:H.a)==null||q.unfix(),(h??(h=new Set)).delete(g))),g.f&li)if(g.f^=li,g===c)La(g,null,t);else{var O=f?f.next:c;g===n.effect.last&&(n.effect.last=g.prev),g.prev&&(g.prev.next=g.next),g.next&&(g.next.prev=g.prev),Vi(n,f,g),Vi(n,g,O),La(g,O,t),f=g,d=[],p=[],c=ba(f.next);continue}if(g!==c){if(u!==void 0&&u.has(g)){if(d.length<p.length){var D=p[0],y;f=D.prev;var B=d[0],R=d[d.length-1];for(y=0;y<d.length;y+=1)La(d[y],D,t);for(y=0;y<p.length;y+=1)u.delete(p[y]);Vi(n,B.prev,R.next),Vi(n,f,B),Vi(n,R,D),c=D,f=R,_-=1,d=[],p=[]}else u.delete(g),La(g,c,t),Vi(n,g.prev,g.next),Vi(n,g,f===null?n.effect.first:f.next),Vi(n,f,g),f=g;continue}for(d=[],p=[];c!==null&&c!==g;)(u??(u=new Set)).add(c),p.push(c),c=ba(c.next);if(c===null)continue}g.f&li||d.push(g),f=g,c=ba(g.next)}if(n.outrogroups!==null){for(const F of n.outrogroups)F.pending.size===0&&(Sl(n,yc(F.done)),(Q=n.outrogroups)==null||Q.delete(F));n.outrogroups.size===0&&(n.outrogroups=null)}if(c!==null||u!==void 0){var C=[];if(u!==void 0)for(g of u)g.f&Ro||C.push(g);for(;c!==null;)!(c.f&Ro)&&c!==n.fallback&&C.push(c),c=ba(c.next);var b=C.length;if(b>0){var A=i&qf&&o===0?t:null;if(a){for(_=0;_<b;_+=1)(T=(G=C[_].nodes)==null?void 0:G.a)==null||T.measure();for(_=0;_<b;_+=1)(I=(w=C[_].nodes)==null?void 0:w.a)==null||I.fix()}Ym(n,C,A)}}a&&Ec(()=>{var F,Y;if(h!==void 0)for(g of h)(Y=(F=g.nodes)==null?void 0:F.a)==null||Y.apply()})}function Zm(n,e,t,i,r,a,o,l){var c=o&sm?o&om?Uu(t):ue(t,!1,!1):null,u=o&lm?Uu(r):null;return{v:c,i:u,e:bl(()=>(a(e,c??t,u??r,l),()=>{n.delete(i)}))}}function La(n,e,t){if(n.nodes)for(var i=n.nodes.start,r=n.nodes.end,a=e&&!(e.f&li)?e.nodes.start:t;i!==null;){var o=Xf(i);if(a.before(i),i===r)return;i=o}}function Vi(n,e,t){e===null?n.effect.first=t:e.next=t,t===null?n.effect.last=e:t.prev=e}function es(n,e,t=!1,i=!1,r=!1,a=!1){var o=n,l="";if(t){var c=n;tn&&(o=Ba(Jr(c)))}me(()=>{var u=Yf;if(l===(l=e()??"")){tn&&Ks();return}if(t&&!tn){u.nodes=null,c.innerHTML=l,l!==""&&To(Jr(c),c.lastChild);return}if(u.nodes!==null&&(mm(u.nodes.start,u.nodes.end),u.nodes=null),l!==""){if(tn){jr.data;for(var f=Ks(),h=f;f!==null&&(f.nodeType!==Gf||f.data!=="");)h=f,f=Xf(f);if(f===null)throw gm(),_m;To(jr,h),o=Ba(f);return}var d=i?xm:r?bm:void 0,p=vm(i?"svg":r?"math":"template",d);p.innerHTML=l;var m=i||r?p:p.content;if(To(Jr(m),m.lastChild),i||r)for(;Jr(m);)o.before(Jr(m));else o.before(m)}})}const Jm=()=>performance.now(),ai={tick:n=>requestAnimationFrame(n),now:()=>Jm(),tasks:new Set};function eh(){const n=ai.now();ai.tasks.forEach(e=>{e.c(n)||(ai.tasks.delete(e),e.f())}),ai.tasks.size!==0&&ai.tick(eh)}function th(n){let e;return ai.tasks.size===0&&ai.tick(eh),{promise:new Promise(t=>{ai.tasks.add(e={c:n,f:t})}),abort(){ai.tasks.delete(e)}}}function hs(n,e){Zf(()=>{n.dispatchEvent(new CustomEvent(e))})}function Qm(n){if(n==="float")return"cssFloat";if(n==="offset")return"cssOffset";if(n.startsWith("--"))return n;const e=n.split("-");return e.length===1?e[0]:e[0]+e.slice(1).map(t=>t[0].toUpperCase()+t.slice(1)).join("")}function Gu(n){const e={},t=n.split(";");for(const i of t){const[r,a]=i.split(":");if(!r||a===void 0)break;const o=Qm(r.trim());e[o]=a.trim()}return e}const jm=n=>n;function pi(n,e,t,i){var D;var r=(n&wm)!==0,a=(n&Am)!==0,o=r&&a,l=(n&Mm)!==0,c=o?"both":r?"in":"out",u,f=e.inert,h=e.style.overflow,d,p;function m(){return Zf(()=>u??(u=t()(e,(i==null?void 0:i())??{},{direction:c})))}var E={is_global:l,in(){var y;if(e.inert=f,!r){p==null||p.abort(),(y=p==null?void 0:p.reset)==null||y.call(p);return}a||d==null||d.abort(),d=yl(e,m(),p,1,()=>{hs(e,"introstart")},()=>{hs(e,"introend"),d==null||d.abort(),d=u=void 0,e.style.overflow=h})},out(y){if(!a){y==null||y(),u=void 0;return}e.inert=!0,p=yl(e,m(),d,0,()=>{hs(e,"outrostart")},()=>{hs(e,"outroend"),y==null||y()})},stop:()=>{d==null||d.abort(),p==null||p.abort()}},g=Yf;if(((D=g.nodes).t??(D.t=[])).push(E),r&&$m){var _=l;if(!_){for(var O=g.parent;O&&O.f&Sm;)for(;(O=O.parent)&&!(O.f&ym););_=!O||(O.f&Em)!==0}_&&Kf(()=>{L(()=>E.in())})}}function yl(n,e,t,i,r,a){var o=i===1;if(Tm(e)){var l,c=!1;return Ec(()=>{if(!c){var _=e({direction:o?"in":"out"});l=yl(n,_,t,i,r,a)}}),{abort:()=>{c=!0,l==null||l.abort()},deactivate:()=>l.deactivate(),reset:()=>l.reset(),t:()=>l.t()}}if(t==null||t.deactivate(),!(e!=null&&e.duration)&&!(e!=null&&e.delay))return r(),a(),{abort:xa,deactivate:xa,reset:xa,t:()=>i};const{delay:u=0,css:f,tick:h,easing:d=jm}=e;var p=[];if(o&&t===void 0&&(h&&h(0,1),f)){var m=Gu(f(0,1));p.push(m,m)}var E=()=>1-i,g=n.animate(p,{duration:u,fill:"forwards"});return g.onfinish=()=>{g.cancel(),r();var _=(t==null?void 0:t.t())??1-i;t==null||t.abort();var O=i-_,D=e.duration*Math.abs(O),y=[];if(D>0){var B=!1;if(f)for(var R=Math.ceil(D/16.666666666666668),C=0;C<=R;C+=1){var b=_+O*d(C/R),A=Gu(f(b,1-b));y.push(A),B||(B=A.overflow==="hidden")}B&&(n.style.overflow="hidden"),E=()=>{var k=g.currentTime;return _+O*d(k/D)},h&&th(()=>{if(g.playState!=="running")return!1;var k=E();return h(k,1-k),!0})}g=n.animate(y,{duration:D,fill:"forwards"}),g.onfinish=()=>{E=()=>i,h==null||h(i,1-i),a()}},{abort:()=>{g&&(g.cancel(),g.effect=null,g.onfinish=xa)},deactivate:()=>{a=xa},reset:()=>{i===0&&(h==null||h(1,0))},t:()=>E()}}const Vu=[...` 	
\r\f \v\uFEFF`];function eg(n,e,t){var i=n==null?"":""+n;if(e&&(i=i?i+" "+e:e),t){for(var r of Object.keys(t))if(t[r])i=i?i+" "+r:r;else if(i.length)for(var a=r.length,o=0;(o=i.indexOf(r,o))>=0;){var l=o+a;(o===0||Vu.includes(i[o-1]))&&(l===i.length||Vu.includes(i[l]))?i=(o===0?"":i.substring(0,o))+i.substring(l+1):o=l}}return i===""?null:i}function Wu(n,e=!1){var t=e?" !important;":";",i="";for(var r of Object.keys(n)){var a=n[r];a!=null&&a!==""&&(i+=" "+r+": "+a+t)}return i}function Co(n){return n[0]!=="-"||n[1]!=="-"?n.toLowerCase():n}function tg(n,e){if(e){var t="",i,r;if(Array.isArray(e)?(i=e[0],r=e[1]):i=e,n){n=String(n).replaceAll(/\s*\/\*.*?\*\/\s*/g,"").trim();var a=!1,o=0,l=!1,c=[];i&&c.push(...Object.keys(i).map(Co)),r&&c.push(...Object.keys(r).map(Co));var u=0,f=-1;const E=n.length;for(var h=0;h<E;h++){var d=n[h];if(l?d==="/"&&n[h-1]==="*"&&(l=!1):a?a===d&&(a=!1):d==="/"&&n[h+1]==="*"?l=!0:d==='"'||d==="'"?a=d:d==="("?o++:d===")"&&o--,!l&&a===!1&&o===0){if(d===":"&&f===-1)f=h;else if(d===";"||h===E-1){if(f!==-1){var p=Co(n.substring(u,f).trim());if(!c.includes(p)){d!==";"&&h++;var m=n.substring(u,h).trim();t+=" "+m+";"}}u=h+1,f=-1}}}}return i&&(t+=Wu(i)),r&&(t+=Wu(r,!0)),t=t.trim(),t===""?null:t}return n==null?null:String(n)}function vt(n,e,t,i,r,a){var o=n[Ou];if(tn||o!==t||o===void 0){var l=eg(t,i,a);(!tn||l!==n.getAttribute("class"))&&(l==null?n.removeAttribute("class"):n.className=l),n[Ou]=t}else if(a&&r!==a)for(var c in a){var u=!!a[c];(r==null||u!==!!r[c])&&n.classList.toggle(c,u)}return a}function Io(n,e={},t,i){for(var r in t){var a=t[r];e[r]!==a&&(t[r]==null?n.style.removeProperty(r):n.style.setProperty(r,a,i))}}function Ln(n,e,t,i){var r=n[Fu];if(tn||r!==e){var a=tg(e,i);(!tn||a!==n.getAttribute("style"))&&(a==null?n.removeAttribute("style"):n.style.cssText=a),n[Fu]=e}else i&&(Array.isArray(i)?(Io(n,t==null?void 0:t[0],i[0]),Io(n,t==null?void 0:t[1],i[1],"important")):Io(n,t,i));return i}function nh(n,e,t=!1){if(n.multiple){if(e==null)return;if(!Vf(e))return Rm();for(var i of n.options)i.selected=e.includes(za(i));return}for(i of n.options){var r=za(i);if(Cm(r,e)){i.selected=!0;return}}(!t||e!==void 0)&&(n.selectedIndex=-1)}function ng(n){var e=new MutationObserver(()=>{nh(n,n.__value)});e.observe(n,{childList:!0,subtree:!0,attributes:!0,attributeFilter:["value"]}),Im(()=>{e.disconnect()})}function Ni(n,e,t=e){var i=new WeakSet,r=!0;Jf(n,"change",a=>{var o=a?"[selected]":":checked",l;if(n.multiple)l=[].map.call(n.querySelectorAll(o),za);else{var c=n.querySelector(o)??n.querySelector("option:not([disabled])");l=c&&za(c)}t(l),n.__value=l,Ti!==null&&i.add(Ti)}),Kf(()=>{var a=e();if(n===document.activeElement){var o=Ti;if(i.has(o))return}if(nh(n,a,r),r&&a===void 0){var l=n.querySelector(":checked");l!==null&&(a=za(l),t(a))}n.__value=a,r=!1}),ng(n)}function za(n){return"__value"in n?n.__value:n.value}const ig=Symbol("is custom element"),rg=Symbol("is html"),ag=Um?"link":"LINK";function gn(n){if(tn){var e=!1,t=()=>{if(!e){if(e=!0,n.hasAttribute("value")){var i=n.value;$t(n,"value",null),n.value=i}if(n.hasAttribute("checked")){var r=n.checked;$t(n,"checked",null),n.checked=r}}};n[Nm]=t,Ec(t),Pm()}}function sg(n,e){var t=ih(n);t.checked!==(t.checked=e??void 0)&&(n.checked=e)}function $t(n,e,t,i){var r=ih(n);tn&&(r[e]=n.getAttribute(e),e==="src"||e==="srcset"||e==="href"&&n.nodeName===ag)||r[e]!==(r[e]=t)&&(e==="loading"&&(n[Lm]=t),t==null?n.removeAttribute(e):typeof t!="string"&&og(n).includes(e)?n[e]=t:n.setAttribute(e,t))}function ih(n){var e;return n[e=Dm]??(n[e]={[ig]:n.nodeName.includes("-"),[rg]:n.namespaceURI===km})}var $u=new Map;function og(n){var e=n.getAttribute("is")||n.nodeName,t=$u.get(e);if(t)return t;$u.set(e,t=[]);for(var i,r=n,a=Element.prototype;a!==r;){i=Fm(r);for(var o in i)i[o].set&&o!=="innerHTML"&&o!=="textContent"&&o!=="innerText"&&t.push(o);r=Om(r)}return t}function nn(n,e,t=e){var i=new WeakSet;Jf(n,"input",async r=>{var a=r?n.defaultValue:n.value;if(a=No(n)?Po(a):a,t(a),Ti!==null&&i.add(Ti),await vr(),a!==(a=e())){var o=n.selectionStart,l=n.selectionEnd,c=n.value.length;if(n.value=a??"",l!==null){var u=n.value.length;o===l&&l===c&&u>c?(n.selectionStart=u,n.selectionEnd=u):(n.selectionStart=o,n.selectionEnd=Math.min(l,u))}}}),(tn&&n.defaultValue!==n.value||L(e)==null&&n.value)&&(t(No(n)?Po(n.value):n.value),Ti!==null&&i.add(Ti)),Bm(()=>{var r=e();if(n===document.activeElement){var a=Ti;if(i.has(a))return}No(n)&&r===Po(n.value)||n.type==="date"&&!r&&!n.value||r!==n.value&&(n.value=r??"")})}function No(n){var e=n.type;return e==="number"||e==="range"}function Po(n){return n===""?null:+n}function rh(n){return function(...e){var t=e[0];t.target===this&&(n==null||n.apply(this,e))}}function ah(n){return function(...e){var t=e[0];return t.stopPropagation(),n==null?void 0:n.apply(this,e)}}function lg(n){return function(...e){var t=e[0];return t.preventDefault(),n==null?void 0:n.apply(this,e)}}function wt(n=!1){const e=zm,t=e.l.u;if(!t)return;let i=()=>tt(e.s);if(n){let r=0,a={};const o=Vm(()=>{let l=!1;const c=e.s;for(const u in c)c[u]!==a[u]&&(a[u]=c[u],l=!0);return l&&r++,r});i=()=>s(o)}t.b.length&&Hm(()=>{Xu(e,i),zu(t.b)}),Bu(()=>{const r=L(()=>t.m.map(Gm));return()=>{for(const a of r)typeof a=="function"&&a()}}),t.a.length&&Bu(()=>{Xu(e,i),zu(t.a)})}function Xu(n,e){if(n.l.s)for(const t of n.l.s)s(t);e()}const cg=n=>n;function sh(n){const e=n-1;return e*e*e+1}function qu(n){const e=typeof n=="string"&&n.match(/^\s*(-?[\d.]+)([^\s]*)\s*$/);return e?[parseFloat(e[1]),e[2]||"px"]:[n,"px"]}function ts(n,{delay:e=0,duration:t=400,easing:i=cg}={}){const r=+getComputedStyle(n).opacity;return{delay:e,duration:t,easing:i,css:a=>`opacity: ${a*r}`}}function ug(n,{delay:e=0,duration:t=400,easing:i=sh,x:r=0,y:a=0,opacity:o=0}={}){const l=getComputedStyle(n),c=+l.opacity,u=l.transform==="none"?"":l.transform,f=c*(1-o),[h,d]=qu(r),[p,m]=qu(a);return{delay:e,duration:t,easing:i,css:(E,g)=>`
			transform: ${u} translate(${(1-E)*h}${d}, ${(1-E)*p}${m});
			opacity: ${c-f*g}`}}function ho(n,{delay:e=0,duration:t=400,easing:i=sh,start:r=0,opacity:a=0}={}){const o=getComputedStyle(n),l=+o.opacity,c=o.transform==="none"?"":o.transform,u=1-r,f=l*(1-a);return{delay:e,duration:t,easing:i,css:(h,d)=>`
			transform: ${c} scale(${1-u*d});
			opacity: ${l-f*d}
		`}}function dg(n){return n}function si(n){const e=n-1;return e*e*e+1}function Yu(n){return Object.prototype.toString.call(n)==="[object Date]"}function El(n,e){if(n===e||n!==n)return()=>n;const t=typeof n;if(t!==typeof e||Array.isArray(n)!==Array.isArray(e))throw new Error("Cannot interpolate values of different type");if(Array.isArray(n)){const i=e.map((r,a)=>El(n[a],r));return r=>i.map(a=>a(r))}if(t==="object"){if(!n||!e)throw new Error("Object cannot be null");if(Yu(n)&&Yu(e)){const a=n.getTime(),l=e.getTime()-a;return c=>new Date(a+c*l)}const i=Object.keys(e),r={};return i.forEach(a=>{r[a]=El(n[a],e[a])}),a=>{const o={};return i.forEach(l=>{o[l]=r[l](a)}),o}}if(t==="number"){const i=e-n;return r=>n+r*i}return()=>e}function ps(n,e={}){const t=_i(n);let i,r=n;function a(o,l){if(r=o,n==null)return t.set(n=o),Promise.resolve();let c=i,u=!1,{delay:f=0,duration:h=400,easing:d=dg,interpolate:p=El}={...e,...l};if(h===0)return c&&(c.abort(),c=null),t.set(n=r),Promise.resolve();const m=ai.now()+f;let E;return i=th(g=>{if(g<m)return!0;u||(E=p(n,o),typeof h=="function"&&(h=h(n,o)),u=!0),c&&(c.abort(),c=null);const _=g-m;return _>h?(t.set(n=o),!1):(t.set(n=E(d(_/h))),!0)}),i.promise}return{set:a,update:(o,l)=>a(o(r,n),l),subscribe:t.subscribe}}let Ku=0;function Tc(n="w"){return Ku+=1,`${n}-${Ku}-${Math.random().toString(36).slice(2,6)}`}function oh(n){return{...n,instanceId:n.instanceId??Tc("i")}}function fg(n){return{kind:"leaf",id:Tc(),app:n}}function Pi(n,e){return n?n.kind==="leaf"?n.id===e?n:null:Pi(n.a,e)??Pi(n.b,e):null}function Zs(n){return n?n.kind==="leaf"?[n]:[...Zs(n.a),...Zs(n.b)]:[]}function Li(n){return n?n.kind==="leaf"?n:Li(n.a)??Li(n.b):null}function wc(n,e,t){const i={};return n&&Da(n,e,t,i),i}function Da(n,e,t,i){if(n.kind==="leaf"){i[n.id]=e;return}if(n.dir==="h"){const r=e.w-t,a=Math.max(40,Math.round(r*n.ratio)),o=Math.max(40,r-a);Da(n.a,{x:e.x,y:e.y,w:a,h:e.h},t,i),Da(n.b,{x:e.x+a+t,y:e.y,w:o,h:e.h},t,i)}else{const r=e.h-t,a=Math.max(40,Math.round(r*n.ratio)),o=Math.max(40,r-a);Da(n.a,{x:e.x,y:e.y,w:e.w,h:a},t,i),Da(n.b,{x:e.x,y:e.y+a+t,w:e.w,h:o},t,i)}}function po(n,e,t,i){const r=fg(i);if(!n)return{root:r,focusId:r.id};if(!e){const o=Li(n);o&&(e=o.id)}return e?{root:Wa(n,e,o=>({kind:"split",dir:t,ratio:.5,a:o,b:r}))??n,focusId:r.id}:{root:{kind:"split",dir:t,ratio:.5,a:n,b:r},focusId:r.id}}function Wa(n,e,t){if(n.kind==="leaf")return n.id===e?t(n):null;const i=Wa(n.a,e,t);if(i)return{...n,a:i};const r=Wa(n.b,e,t);return r?{...n,b:r}:null}function Ac(n,e){var r;if(!n)return{root:null,focusId:null};if(n.kind==="leaf")return n.id===e?{root:null,focusId:null}:{root:n,focusId:e};const t=Ml(n,e);if(t===null)return{root:null,focusId:null};if(t===n)return{root:n,focusId:e};const i=((r=Li(t))==null?void 0:r.id)??null;return{root:t,focusId:i}}function Ml(n,e){if(n.kind==="leaf")return n.id===e?null:n;const t=Ml(n.a,e);if(t===null)return n.b;if(t!==n.a)return{...n,a:t};const i=Ml(n.b,e);return i===null?n.a:i!==n.b?{...n,b:i}:n}function hg(n,e,t){if(e===t)return n;const i=Pi(n,e),r=Pi(n,t);if(!i||!r)return n;let a=Wa(n,e,()=>r)??n;return a=Wa(a,t,()=>i)??a,a}function lh(n,e,t,i,r){if(!n)return null;const a=wc(n,e,t);if(!i||!a[i]){const f=Li(n);return(f==null?void 0:f.id)??null}const o=a[i],l=o.x+o.w/2,c=o.y+o.h/2;let u=null;for(const[f,h]of Object.entries(a)){if(f===i)continue;const d=h.x+h.w/2,p=h.y+h.h/2;if(r==="left"&&d>=l-1||r==="right"&&d<=l+1||r==="up"&&p>=c-1||r==="down"&&p<=c+1)continue;const m=Math.abs(r==="left"||r==="right"?d-l:p-c),E=Math.abs(r==="left"||r==="right"?p-c:d-l),g=m+E*.5;(!u||g<u.d)&&(u={id:f,d:g})}return(u==null?void 0:u.id)??i}function pg(n,e,t,i,r){if(!n||!i)return n;const a=lh(n,e,t,i,r);return!a||a===i?n:hg(n,i,a)}function mg(n=10){const e=[];for(let t=1;t<=n;t+=1)e.push({id:t,root:null,focusId:null,floating:[]});return e}function Zu(n){return n.root===null&&n.floating.length===0}const gg={workspaces:mg(10),activeWs:1},Un=_i(gg),da=_i({x:0,y:0,w:1280,h:720}),ns=_i(8),Mr=ja(Un,n=>n.workspaces[n.activeWs-1]),Tl=new Set;function Rc(n){return Tl.add(n),()=>Tl.delete(n)}function ch(n){if(n)for(const e of Tl)try{e(n)}catch{}}ja(Mr,n=>(n==null?void 0:n.focusId)??null);const _g=ja([Mr,da,ns],([n,e,t])=>n?wc(n.root,e,t):{}),uh=ja(Mr,n=>n?Zs(n.root):[]),vg=ja(Mr,n=>(n==null?void 0:n.floating)??[]);function Di(n){Un.update(e=>{const t=e.workspaces.slice();return t[e.activeWs-1]=n(t[e.activeWs-1]),{...e,workspaces:t}})}function Cc(n){n<1||n>10||Un.update(e=>({...e,activeWs:n}))}function xg(n){if(n<1||n>10)return;const e=qn(Un);if(e.activeWs===n)return;const t=e.workspaces[e.activeWs-1];if(!t.focusId)return;const i=Pi(t.root,t.focusId);if(!i)return;const{root:r,focusId:a}=Ac(t.root,t.focusId),o=e.workspaces[n-1],{root:l,focusId:c}=po(o.root,o.focusId,"h",i.app),u=e.workspaces.slice();u[e.activeWs-1]={...t,root:r,focusId:a},u[n-1]={...o,root:l,focusId:c},Un.set({...e,workspaces:u})}function gr(n,e="h"){const t=oh(n);Di(i=>{const{root:r,focusId:a}=po(i.root,i.focusId,e,t);return{...i,root:r,focusId:a}})}function Ha(){let n;Di(e=>{var o,l,c;if(!e.focusId)return e;const t=e.floating.find(u=>u.id===e.focusId);if(t){n=t.app.instanceId;const u=e.floating.filter(f=>f.id!==e.focusId);return{...e,floating:u,focusId:((o=u[u.length-1])==null?void 0:o.id)??((l=Li(e.root))==null?void 0:l.id)??null}}const i=Pi(e.root,e.focusId);n=i==null?void 0:i.app.instanceId;const{root:r,focusId:a}=Ac(e.root,e.focusId);return{...e,root:r,focusId:a??((c=Li(r))==null?void 0:c.id)??null}}),ch(n)}function Js(n){Di(e=>({...e,focusId:n}))}function bg(n){const e=qn(Un),t=qn(da),i=qn(ns),r=e.workspaces[e.activeWs-1],a=lh(r.root,t,i,r.focusId,n);a&&a!==r.focusId&&Js(a)}function Sg(n){const e=qn(Un),t=qn(da),i=qn(ns),r=e.workspaces[e.activeWs-1];if(!r.focusId)return;const a=pg(r.root,t,i,r.focusId,n);a&&a!==r.root&&Di(o=>({...o,root:a}))}let Qs=0;function yg(n,e){if(e)return{x:Math.max(n.x,e.x+16),y:Math.max(n.y,e.y+16),w:Math.min(900,Math.max(360,e.w)),h:Math.min(600,Math.max(240,e.h))};const t=Math.min(820,Math.max(360,n.w*.5)),i=Math.min(560,Math.max(240,n.h*.6));return{x:n.x+(n.w-t)/2,y:n.y+(n.h-i)/2,w:t,h:i}}function Eg(){var h;const n=qn(Un),e=qn(da),t=qn(ns),i=n.workspaces[n.activeWs-1];if(!i.focusId)return;const r=i.floating.find(d=>d.id===i.focusId);if(r){const{root:d,focusId:p}=po(i.root,((h=Li(i.root))==null?void 0:h.id)??null,"h",r.app);Di(m=>({...m,root:d,focusId:p,floating:m.floating.filter(E=>E.id!==r.id)}));return}const a=Pi(i.root,i.focusId);if(!a)return;const l=wc(i.root,e,t)[a.id],{root:c}=Ac(i.root,a.id);Qs+=1;const u=yg(e,l),f={id:Tc("f"),app:a.app,x:u.x,y:u.y,w:u.w,h:u.h,z:Qs};Di(d=>({...d,root:c,focusId:f.id,floating:[...d.floating,f]}))}function Mg(n,e){Di(t=>({...t,floating:t.floating.map(i=>i.id===n?{...i,...e}:i)}))}function Ju(n){Qs+=1;const e=Qs;Di(t=>({...t,focusId:n,floating:t.floating.map(i=>i.id===n?{...i,z:e}:i)}))}function Tg(n){let e;Di(t=>{var r;const i=t.floating.find(a=>a.id===n);return e=i==null?void 0:i.app.instanceId,{...t,focusId:t.focusId===n?((r=Li(t.root))==null?void 0:r.id)??null:t.focusId,floating:t.floating.filter(a=>a.id!==n)}}),ch(e)}function wg(n=[]){Un.update(e=>{const t=e.workspaces.slice();for(const i of n){const r=i.workspace??e.activeWs,a=t[r-1],o=oh(i.app),{root:l,focusId:c}=po(a.root,a.focusId,i.dir??"h",o);t[r-1]={...a,root:l,focusId:c}}return{...e,workspaces:t}})}const Ic=_i([]);let Qu=0;function mt(n){Qu+=1;const e=`t-${Qu}`,t={id:e,title:n.title,body:n.body,kind:n.kind??"info",createdAt:performance.now(),ttlMs:n.ttlMs??3500};return Ic.update(i=>[...i,t]),t.ttlMs>0&&setTimeout(()=>dh(e),t.ttlMs),e}function dh(n){Ic.update(e=>e.filter(t=>t.id!==n))}const mo="";function Nc(n,e){if(typeof window>"u")return"";const t=window.location.protocol==="https:"?"wss:":"ws:",i=e?"?"+Object.entries(e).map(([r,a])=>`${encodeURIComponent(r)}=${encodeURIComponent(String(a))}`).join("&"):"";return`${t}//${window.location.host}${n}${i}`}async function dt(n,e={}){const t=await fetch(mo+n,{...e,headers:{"content-type":"application/json",...e.headers??{}}});if(!t.ok){const i=await t.text().catch(()=>"");throw new Error(`${t.status} ${t.statusText}: ${i.slice(0,200)}`)}return t.json()}function Ag(n){const e={};n.cwd&&(e.cwd=n.cwd),n.cols&&(e.cols=n.cols),n.rows&&(e.rows=n.rows);const t=new WebSocket(Nc("/zeus-os/pty",e));t.onmessage=r=>{var a;try{const o=JSON.parse(r.data);o.type==="output"&&typeof o.data=="string"?n.onOutput(o.data):o.type==="exit"&&((a=n.onExit)==null||a.call(n,typeof o.code=="number"?o.code:-1))}catch{}};function i(r){t.readyState===WebSocket.OPEN?t.send(JSON.stringify(r)):t.addEventListener("open",()=>t.send(JSON.stringify(r)),{once:!0})}return{send(r){i({type:"input",data:r})},resize(r,a){i({type:"resize",cols:r,rows:a})},close(){try{t.close()}catch{}}}}let js=0;const $a=new Map,Xa=new Map;function go(n,e){return`${n}::${e}`}function qa(n){let e=$a.get(n);if(!e){js+=1;const t=`t-${js}`;e={tabs:[{id:t,label:"shell"}],activeTabId:t},$a.set(n,e)}return e}function ju(n){const e=qa(n);js+=1;const t={id:`t-${js}`,label:"shell"};return e.tabs=[...e.tabs,t],e.activeTabId=t.id,t}function Rg(n,e){const t=qa(n);t.activeTabId=e}function Cg(n,e){var i;const t=qa(n);return t.tabs=t.tabs.filter(r=>r.id!==e),t.activeTabId===e&&(t.activeTabId=((i=t.tabs[t.tabs.length-1])==null?void 0:i.id)??null),fh(go(n,e)),t.tabs.length===0&&$a.delete(n),t.tabs}function fh(n){const e=Xa.get(n);if(e){try{e.pty.close()}catch{}try{e.term.dispose()}catch{}try{e.container.remove()}catch{}Xa.delete(n)}}async function Ig(n,e,t,i={}){const r=go(n,e),a=Xa.get(r);if(a)return t.appendChild(a.container),queueMicrotask(()=>{try{a.fit.fit()}catch{}}),{fit:()=>ed(a.fit)};const{Terminal:o}=await Pa(async()=>{const{Terminal:p}=await import("../chunks/BtnXY879.js").then(m=>m.x);return{Terminal:p}},[]),{FitAddon:l}=await Pa(async()=>{const{FitAddon:p}=await import("../chunks/CyyJcX4C.js").then(m=>m.a);return{FitAddon:p}},[]),{WebLinksAddon:c}=await Pa(async()=>{const{WebLinksAddon:p}=await import("../chunks/CmYOsrza.js").then(m=>m.a);return{WebLinksAddon:p}},[]);await Pa(()=>Promise.resolve({}),__vite__mapDeps([0]));const u=document.createElement("div");u.className="h-full w-full p-1 font-mono";const f=new o({fontFamily:"JetBrains Mono, ui-monospace, monospace",fontSize:13,cursorBlink:!0,allowProposedApi:!0,scrollback:5e3,theme:Pg()}),h=new l;f.loadAddon(h),f.loadAddon(new c),t.appendChild(u),f.open(u);try{h.fit()}catch{}const d=Ag({cols:f.cols,rows:f.rows,onOutput:p=>f.write(p),onExit:p=>{var m;try{f.writeln(""),f.writeln(`\x1B[2m[process exited (${p})]\x1B[0m`)}catch{}(m=i.onExit)==null||m.call(i,p)}});return f.onData(p=>d.send(p)),f.onResize(({cols:p,rows:m})=>d.resize(p,m)),Xa.set(r,{container:u,term:f,fit:h,pty:d,initialized:!0}),{fit:()=>ed(h)}}function Ng(n,e,t){const i=go(n,e),r=Xa.get(i);r&&t&&r.container.parentElement===t&&t.removeChild(r.container)}function ed(n){try{n.fit()}catch{}}function Pg(){const n=getComputedStyle(document.documentElement),e=t=>{const i=n.getPropertyValue(t).trim();if(!i)return;const[r,a,o]=i.split(/\s+/).map(Number);return`#${[r,a,o].map(l=>l.toString(16).padStart(2,"0")).join("")}`};return{background:e("--surface")??"#1e1e2e",foreground:e("--fg")??"#cdd6f4",cursor:e("--accent")??"#89b4fa"}}Rc(n=>{const e=$a.get(n);if(e){for(const t of e.tabs)fh(go(n,t.id));$a.delete(n)}});var Lg=ie('<div class="h-full w-full"></div>');function Dg(n,e){Mt(e,!1);let t=ft(e,"instanceId",8),i=ft(e,"tabId",8),r=ft(e,"visible",8,!0),a=ft(e,"onExit",8,void 0),o=ue(),l=ue(null),c=null,u=!1;async function f(){var p;if(!(!s(o)||u))try{const{fit:m}=await Ig(t(),i(),s(o),{onExit:a()});W(l,m),u=!0,await vr(),(p=s(l))==null||p()}catch(m){mt({title:"Terminal failed to start",body:String(m),kind:"err"})}}zt(()=>{f(),c=new ResizeObserver(()=>{var p;r()&&((p=s(l))==null||p())}),s(o)&&c.observe(s(o))}),Jt(()=>{c==null||c.disconnect(),Ng(t(),i(),s(o)),u=!1}),lt(()=>(tt(r()),s(l)),()=>{r()&&s(l)&&queueMicrotask(()=>{var p;return(p=s(l))==null?void 0:p()})}),Ht(),wt();var h=Lg();let d;Er(h,p=>W(o,p),()=>s(o)),me(()=>d=Ln(h,"",d,{display:r()?"":"none"})),j(n,h),Tt()}var kg=ie('<button><span> </span> <span class="opacity-50 hover:opacity-100 hover:text-err" role="button" tabindex="0">×</span></button>'),Ug=ie('<div class="flex items-center px-1 py-0.5 text-xs font-mono select-none border-b border-border/30" style="background: rgb(var(--surface-2) / 0.5);"><!> <button class="px-2 py-1 text-muted hover:text-fg" title="New tab (Ctrl+Shift+T)">+</button></div>'),Og=ie('<div class="absolute inset-0"><!></div>'),Fg=ie('<button class="absolute top-1 right-1 z-10 text-muted hover:text-fg text-xs font-mono px-1 opacity-50 hover:opacity-100" title="New tab (Ctrl+Shift+T)">+</button>'),Bg=ie('<div class="h-full w-full flex flex-col"><!> <div class="flex-1 min-h-0 relative"></div> <!></div>');function Pc(n,e){var O;Mt(e,!1);let t=ft(e,"app",8),i=qa(t().instanceId),r=ue(i.tabs),a=ue(i.activeTabId??((O=s(r)[0])==null?void 0:O.id)??"");function o(){var D;i=qa(t().instanceId),W(r,i.tabs),W(a,i.activeTabId??((D=s(r)[0])==null?void 0:D.id)??"")}function l(){ju(t().instanceId),o()}function c(D){Cg(t().instanceId,D).length===0&&ju(t().instanceId),o()}function u(D){Rg(t().instanceId,D),W(a,D)}function f(D){return()=>c(D)}function h(D){!(D.metaKey||D.ctrlKey)||!D.shiftKey||(D.key.toLowerCase()==="t"?(D.preventDefault(),l()):D.key.toLowerCase()==="w"&&(D.preventDefault(),c(s(a))))}wt();var d=Bg();Re("keydown",Qf,h);var p=M(d);{var m=D=>{var y=Ug(),B=M(y);ct(B,3,()=>s(r),C=>C.id,(C,b,A)=>{var k=kg();let z;var H=M(k),q=M(H);S(H);var Q=U(H,2);S(k),me(()=>{z=vt(k,1,"px-2 py-1 rounded-t-md mr-1 flex items-center gap-1 transition-colors",null,z,{"bg-surface":s(b).id===s(a),"text-fg":s(b).id===s(a),"text-muted":s(b).id!==s(a)}),ee(q,`${s(b),L(()=>s(b).label)??""} ${s(A)+1}`)}),Re("click",Q,ah(()=>c(s(b).id))),Re("keydown",Q,G=>G.key==="Enter"&&c(s(b).id)),Re("click",k,()=>u(s(b).id)),j(C,k)});var R=U(B,2);S(y),Re("click",R,l),j(D,y)};Ae(p,D=>{s(r),L(()=>s(r).length>1)&&D(m)})}var E=U(p,2);ct(E,5,()=>s(r),D=>D.id,(D,y)=>{var B=Og(),R=M(B);{let C=tr(()=>(s(y),s(a),L(()=>s(y).id===s(a)))),b=tr(()=>(s(y),L(()=>f(s(y).id))));Dg(R,{get instanceId(){return tt(t()),L(()=>t().instanceId)},get tabId(){return s(y),L(()=>s(y).id)},get visible(){return s(C)},get onExit(){return s(b)}})}S(B),j(D,B)}),S(E);var g=U(E,2);{var _=D=>{var y=Fg();Re("click",y,l),j(D,y)};Ae(g,D=>{s(r),L(()=>s(r).length===1)&&D(_)})}S(d),j(n,d),Tt()}async function zg(n){var o;const e=JSON.stringify({message:n.message,session_id:n.sessionId??void 0,use_context:!0}),t=await fetch(mo+"/chat/stream",{method:"POST",headers:{"content-type":"application/json"},body:e,signal:n.signal});if(!t.ok||!t.body){const l=await t.text().catch(()=>"");(o=n.onError)==null||o.call(n,`${t.status} ${t.statusText}: ${l.slice(0,200)}`);return}const i=t.body.getReader(),r=new TextDecoder("utf-8");let a="";for(;;){const{value:l,done:c}=await i.read();if(c)break;a+=r.decode(l,{stream:!0});let u;for(;(u=a.indexOf(`

`))!==-1;){const f=a.slice(0,u);a=a.slice(u+2),Hg(f,n)}}}function Hg(n,e){var r,a,o;const t=n.split(`
`);let i="";for(const l of t)l.startsWith(":")||l.startsWith("data:")&&(i+=l.slice(5).trimStart());if(i)try{const l=JSON.parse(i);l.type==="token"&&typeof l.content=="string"?e.onToken(l.content):l.type==="phase"&&typeof l.detail=="string"?(r=e.onPhase)==null||r.call(e,l.detail):l.type==="done"?(a=e.onDone)==null||a.call(e,l):l.type==="error"&&typeof l.detail=="string"&&((o=e.onError)==null||o.call(e,l.detail))}catch{}}/*! @license DOMPurify 3.4.7 | (c) Cure53 and other contributors | Released under the Apache license 2.0 and Mozilla Public License 2.0 | github.com/cure53/DOMPurify/blob/3.4.7/LICENSE */function td(n,e){(e==null||e>n.length)&&(e=n.length);for(var t=0,i=Array(e);t<e;t++)i[t]=n[t];return i}function Gg(n){if(Array.isArray(n))return n}function Vg(n,e){var t=n==null?null:typeof Symbol<"u"&&n[Symbol.iterator]||n["@@iterator"];if(t!=null){var i,r,a,o,l=[],c=!0,u=!1;try{if(a=(t=t.call(n)).next,e!==0)for(;!(c=(i=a.call(t)).done)&&(l.push(i.value),l.length!==e);c=!0);}catch(f){u=!0,r=f}finally{try{if(!c&&t.return!=null&&(o=t.return(),Object(o)!==o))return}finally{if(u)throw r}}return l}}function Wg(){throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function $g(n,e){return Gg(n)||Vg(n,e)||Xg(n,e)||Wg()}function Xg(n,e){if(n){if(typeof n=="string")return td(n,e);var t={}.toString.call(n).slice(8,-1);return t==="Object"&&n.constructor&&(t=n.constructor.name),t==="Map"||t==="Set"?Array.from(n):t==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)?td(n,e):void 0}}const hh=Object.entries,nd=Object.setPrototypeOf,qg=Object.isFrozen,Yg=Object.getPrototypeOf,Kg=Object.getOwnPropertyDescriptor;let vn=Object.freeze,On=Object.seal,Qr=Object.create,ph=typeof Reflect<"u"&&Reflect,wl=ph.apply,Al=ph.construct;vn||(vn=function(e){return e});On||(On=function(e){return e});wl||(wl=function(e,t){for(var i=arguments.length,r=new Array(i>2?i-2:0),a=2;a<i;a++)r[a-2]=arguments[a];return e.apply(t,r)});Al||(Al=function(e){for(var t=arguments.length,i=new Array(t>1?t-1:0),r=1;r<t;r++)i[r-1]=arguments[r];return new e(...i)});const Pr=Zt(Array.prototype.forEach),Zg=Zt(Array.prototype.lastIndexOf),id=Zt(Array.prototype.pop),Lr=Zt(Array.prototype.push),Jg=Zt(Array.prototype.splice),pn=Array.isArray,ka=Zt(String.prototype.toLowerCase),Lo=Zt(String.prototype.toString),rd=Zt(String.prototype.match),Dr=Zt(String.prototype.replace),ad=Zt(String.prototype.indexOf),Qg=Zt(String.prototype.trim),jg=Zt(Number.prototype.toString),e_=Zt(Boolean.prototype.toString),sd=typeof BigInt>"u"?null:Zt(BigInt.prototype.toString),od=typeof Symbol>"u"?null:Zt(Symbol.prototype.toString),Wt=Zt(Object.prototype.hasOwnProperty),Sa=Zt(Object.prototype.toString),rn=Zt(RegExp.prototype.test),ya=t_(TypeError);function Zt(n){return function(e){e instanceof RegExp&&(e.lastIndex=0);for(var t=arguments.length,i=new Array(t>1?t-1:0),r=1;r<t;r++)i[r-1]=arguments[r];return wl(n,e,i)}}function t_(n){return function(){for(var e=arguments.length,t=new Array(e),i=0;i<e;i++)t[i]=arguments[i];return Al(n,t)}}function gt(n,e){let t=arguments.length>2&&arguments[2]!==void 0?arguments[2]:ka;if(nd&&nd(n,null),!pn(e))return n;let i=e.length;for(;i--;){let r=e[i];if(typeof r=="string"){const a=t(r);a!==r&&(qg(e)||(e[i]=a),r=a)}n[r]=!0}return n}function n_(n){for(let e=0;e<n.length;e++)Wt(n,e)||(n[e]=null);return n}function cn(n){const e=Qr(null);for(const i of hh(n)){var t=$g(i,2);const r=t[0],a=t[1];Wt(n,r)&&(pn(a)?e[r]=n_(a):a&&typeof a=="object"&&a.constructor===Object?e[r]=cn(a):e[r]=a)}return e}function i_(n){switch(typeof n){case"string":return n;case"number":return jg(n);case"boolean":return e_(n);case"bigint":return sd?sd(n):"0";case"symbol":return od?od(n):"Symbol()";case"undefined":return Sa(n);case"function":case"object":{if(n===null)return Sa(n);const e=n,t=ni(e,"toString");if(typeof t=="function"){const i=t(e);return typeof i=="string"?i:Sa(i)}return Sa(n)}default:return Sa(n)}}function ni(n,e){for(;n!==null;){const i=Kg(n,e);if(i){if(i.get)return Zt(i.get);if(typeof i.value=="function")return Zt(i.value)}n=Yg(n)}function t(){return null}return t}function r_(n){try{return rn(n,""),!0}catch{return!1}}const ld=vn(["a","abbr","acronym","address","area","article","aside","audio","b","bdi","bdo","big","blink","blockquote","body","br","button","canvas","caption","center","cite","code","col","colgroup","content","data","datalist","dd","decorator","del","details","dfn","dialog","dir","div","dl","dt","element","em","fieldset","figcaption","figure","font","footer","form","h1","h2","h3","h4","h5","h6","head","header","hgroup","hr","html","i","img","input","ins","kbd","label","legend","li","main","map","mark","marquee","menu","menuitem","meter","nav","nobr","ol","optgroup","option","output","p","picture","pre","progress","q","rp","rt","ruby","s","samp","search","section","select","shadow","slot","small","source","spacer","span","strike","strong","style","sub","summary","sup","table","tbody","td","template","textarea","tfoot","th","thead","time","tr","track","tt","u","ul","var","video","wbr"]),Do=vn(["svg","a","altglyph","altglyphdef","altglyphitem","animatecolor","animatemotion","animatetransform","circle","clippath","defs","desc","ellipse","enterkeyhint","exportparts","filter","font","g","glyph","glyphref","hkern","image","inputmode","line","lineargradient","marker","mask","metadata","mpath","part","path","pattern","polygon","polyline","radialgradient","rect","stop","style","switch","symbol","text","textpath","title","tref","tspan","view","vkern"]),ko=vn(["feBlend","feColorMatrix","feComponentTransfer","feComposite","feConvolveMatrix","feDiffuseLighting","feDisplacementMap","feDistantLight","feDropShadow","feFlood","feFuncA","feFuncB","feFuncG","feFuncR","feGaussianBlur","feImage","feMerge","feMergeNode","feMorphology","feOffset","fePointLight","feSpecularLighting","feSpotLight","feTile","feTurbulence"]),a_=vn(["animate","color-profile","cursor","discard","font-face","font-face-format","font-face-name","font-face-src","font-face-uri","foreignobject","hatch","hatchpath","mesh","meshgradient","meshpatch","meshrow","missing-glyph","script","set","solidcolor","unknown","use"]),Uo=vn(["math","menclose","merror","mfenced","mfrac","mglyph","mi","mlabeledtr","mmultiscripts","mn","mo","mover","mpadded","mphantom","mroot","mrow","ms","mspace","msqrt","mstyle","msub","msup","msubsup","mtable","mtd","mtext","mtr","munder","munderover","mprescripts"]),s_=vn(["maction","maligngroup","malignmark","mlongdiv","mscarries","mscarry","msgroup","mstack","msline","msrow","semantics","annotation","annotation-xml","mprescripts","none"]),cd=vn(["#text"]),ud=vn(["accept","action","align","alt","autocapitalize","autocomplete","autopictureinpicture","autoplay","background","bgcolor","border","capture","cellpadding","cellspacing","checked","cite","class","clear","color","cols","colspan","command","commandfor","controls","controlslist","coords","crossorigin","datetime","decoding","default","dir","disabled","disablepictureinpicture","disableremoteplayback","download","draggable","enctype","enterkeyhint","exportparts","face","for","headers","height","hidden","high","href","hreflang","id","inert","inputmode","integrity","ismap","kind","label","lang","list","loading","loop","low","max","maxlength","media","method","min","minlength","multiple","muted","name","nonce","noshade","novalidate","nowrap","open","optimum","part","pattern","placeholder","playsinline","popover","popovertarget","popovertargetaction","poster","preload","pubdate","radiogroup","readonly","rel","required","rev","reversed","role","rows","rowspan","spellcheck","scope","selected","shape","size","sizes","slot","span","srclang","start","src","srcset","step","style","summary","tabindex","title","translate","type","usemap","valign","value","width","wrap","xmlns"]),Oo=vn(["accent-height","accumulate","additive","alignment-baseline","amplitude","ascent","attributename","attributetype","azimuth","basefrequency","baseline-shift","begin","bias","by","class","clip","clippathunits","clip-path","clip-rule","color","color-interpolation","color-interpolation-filters","color-profile","color-rendering","cx","cy","d","dx","dy","diffuseconstant","direction","display","divisor","dur","edgemode","elevation","end","exponent","fill","fill-opacity","fill-rule","filter","filterunits","flood-color","flood-opacity","font-family","font-size","font-size-adjust","font-stretch","font-style","font-variant","font-weight","fx","fy","g1","g2","glyph-name","glyphref","gradientunits","gradienttransform","height","href","id","image-rendering","in","in2","intercept","k","k1","k2","k3","k4","kerning","keypoints","keysplines","keytimes","lang","lengthadjust","letter-spacing","kernelmatrix","kernelunitlength","lighting-color","local","marker-end","marker-mid","marker-start","markerheight","markerunits","markerwidth","maskcontentunits","maskunits","max","mask","mask-type","media","method","mode","min","name","numoctaves","offset","operator","opacity","order","orient","orientation","origin","overflow","paint-order","path","pathlength","patterncontentunits","patterntransform","patternunits","points","preservealpha","preserveaspectratio","primitiveunits","r","rx","ry","radius","refx","refy","repeatcount","repeatdur","restart","result","rotate","scale","seed","shape-rendering","slope","specularconstant","specularexponent","spreadmethod","startoffset","stddeviation","stitchtiles","stop-color","stop-opacity","stroke-dasharray","stroke-dashoffset","stroke-linecap","stroke-linejoin","stroke-miterlimit","stroke-opacity","stroke","stroke-width","style","surfacescale","systemlanguage","tabindex","tablevalues","targetx","targety","transform","transform-origin","text-anchor","text-decoration","text-rendering","textlength","type","u1","u2","unicode","values","viewbox","visibility","version","vert-adv-y","vert-origin-x","vert-origin-y","width","word-spacing","wrap","writing-mode","xchannelselector","ychannelselector","x","x1","x2","xmlns","y","y1","y2","z","zoomandpan"]),dd=vn(["accent","accentunder","align","bevelled","close","columnalign","columnlines","columnspacing","columnspan","denomalign","depth","dir","display","displaystyle","encoding","fence","frame","height","href","id","largeop","length","linethickness","lquote","lspace","mathbackground","mathcolor","mathsize","mathvariant","maxsize","minsize","movablelimits","notation","numalign","open","rowalign","rowlines","rowspacing","rowspan","rspace","rquote","scriptlevel","scriptminsize","scriptsizemultiplier","selection","separator","separators","stretchy","subscriptshift","supscriptshift","symmetric","voffset","width","xmlns"]),ms=vn(["xlink:href","xml:id","xlink:title","xml:space","xmlns:xlink"]),o_=On(/{{[\w\W]*|^[\w\W]*}}/g),l_=On(/<%[\w\W]*|^[\w\W]*%>/g),c_=On(/\${[\w\W]*/g),u_=On(/^data-[\-\w.\u00B7-\uFFFF]+$/),d_=On(/^aria-[\-\w]+$/),fd=On(/^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|matrix):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i),f_=On(/^(?:\w+script|data):/i),h_=On(/[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g),p_=On(/^html$/i),m_=On(/^[a-z][.\w]*(-[.\w]+)+$/i),Qn={element:1,attribute:2,text:3,cdataSection:4,entityReference:5,entityNode:6,progressingInstruction:7,comment:8,document:9,documentType:10,documentFragment:11,notation:12},g_=function(){return typeof window>"u"?null:window},__=function(e,t){if(typeof e!="object"||typeof e.createPolicy!="function")return null;let i=null;const r="data-tt-policy-suffix";t&&t.hasAttribute(r)&&(i=t.getAttribute(r));const a="dompurify"+(i?"#"+i:"");try{return e.createPolicy(a,{createHTML(o){return o},createScriptURL(o){return o}})}catch{return console.warn("TrustedTypes policy "+a+" could not be created."),null}},hd=function(){return{afterSanitizeAttributes:[],afterSanitizeElements:[],afterSanitizeShadowDOM:[],beforeSanitizeAttributes:[],beforeSanitizeElements:[],beforeSanitizeShadowDOM:[],uponSanitizeAttribute:[],uponSanitizeElement:[],uponSanitizeShadowNode:[]}};function mh(){let n=arguments.length>0&&arguments[0]!==void 0?arguments[0]:g_();const e=it=>mh(it);if(e.version="3.4.7",e.removed=[],!n||!n.document||n.document.nodeType!==Qn.document||!n.Element)return e.isSupported=!1,e;let t=n.document;const i=t,r=i.currentScript;n.DocumentFragment;const a=n.HTMLTemplateElement,o=n.Node,l=n.Element,c=n.NodeFilter,u=n.NamedNodeMap;u===void 0&&(n.NamedNodeMap||n.MozNamedAttrMap),n.HTMLFormElement;const f=n.DOMParser,h=n.trustedTypes,d=l.prototype,p=ni(d,"cloneNode"),m=ni(d,"remove"),E=ni(d,"nextSibling"),g=ni(d,"childNodes"),_=ni(d,"parentNode"),O=ni(d,"shadowRoot"),D=ni(d,"attributes"),y=o&&o.prototype?ni(o.prototype,"nodeType"):null,B=o&&o.prototype?ni(o.prototype,"nodeName"):null;if(typeof a=="function"){const it=t.createElement("template");it.content&&it.content.ownerDocument&&(t=it.content.ownerDocument)}let R,C="";const b=t,A=b.implementation,k=b.createNodeIterator,z=b.createDocumentFragment,H=b.getElementsByTagName,q=i.importNode;let Q=hd();e.isSupported=typeof hh=="function"&&typeof _=="function"&&A&&A.createHTMLDocument!==void 0;const G=o_,T=l_,w=c_,I=u_,F=d_,Y=f_,te=h_,X=m_;let K=fd,se=null;const ne=gt({},[...ld,...Do,...ko,...Uo,...cd]);let N=null;const V=gt({},[...ud,...Oo,...dd,...ms]);let re=Object.seal(Qr(null,{tagNameCheck:{writable:!0,configurable:!1,enumerable:!0,value:null},attributeNameCheck:{writable:!0,configurable:!1,enumerable:!0,value:null},allowCustomizedBuiltInElements:{writable:!0,configurable:!1,enumerable:!0,value:!1}})),Me=null,fe=null;const oe=Object.seal(Qr(null,{tagCheck:{writable:!0,configurable:!1,enumerable:!0,value:null},attributeCheck:{writable:!0,configurable:!1,enumerable:!0,value:null}}));let ve=!0,ye=!0,Ie=!1,be=!0,ke=!1,xe=!0,Ee=!1,_e=!1,De=!1,Ne=!1,Oe=!1,J=!1,We=!0,Fe=!1;const P="user-content-";let x=!0,Z=!1,ae={},de=null;const Le=gt({},["annotation-xml","audio","colgroup","desc","foreignobject","head","iframe","math","mi","mn","mo","ms","mtext","noembed","noframes","noscript","plaintext","script","style","svg","template","thead","title","video","xmp"]);let He=null;const Se=gt({},["audio","video","img","source","image","track"]);let we=null;const Ge=gt({},["alt","class","for","id","label","name","pattern","placeholder","role","summary","title","value","style","xmlns"]),Je="http://www.w3.org/1998/Math/MathML",Pe="http://www.w3.org/2000/svg",Ce="http://www.w3.org/1999/xhtml";let qe=Ce,je=!1,st=null;const ce=gt({},[Je,Pe,Ce],Lo);let Be=gt({},["mi","mo","mn","ms","mtext"]),Te=gt({},["annotation-xml"]);const Ve=gt({},["title","style","font","a","script"]);let Ye=null;const Ue=["application/xhtml+xml","text/html"],nt="text/html";let $e=null,It=null;const yt=t.createElement("form"),Mn=function(v){return v instanceof RegExp||v instanceof Function},xn=function(){let v=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};if(It&&It===v)return;(!v||typeof v!="object")&&(v={}),v=cn(v),Ye=Ue.indexOf(v.PARSER_MEDIA_TYPE)===-1?nt:v.PARSER_MEDIA_TYPE,$e=Ye==="application/xhtml+xml"?Lo:ka,se=Wt(v,"ALLOWED_TAGS")&&pn(v.ALLOWED_TAGS)?gt({},v.ALLOWED_TAGS,$e):ne,N=Wt(v,"ALLOWED_ATTR")&&pn(v.ALLOWED_ATTR)?gt({},v.ALLOWED_ATTR,$e):V,st=Wt(v,"ALLOWED_NAMESPACES")&&pn(v.ALLOWED_NAMESPACES)?gt({},v.ALLOWED_NAMESPACES,Lo):ce,we=Wt(v,"ADD_URI_SAFE_ATTR")&&pn(v.ADD_URI_SAFE_ATTR)?gt(cn(Ge),v.ADD_URI_SAFE_ATTR,$e):Ge,He=Wt(v,"ADD_DATA_URI_TAGS")&&pn(v.ADD_DATA_URI_TAGS)?gt(cn(Se),v.ADD_DATA_URI_TAGS,$e):Se,de=Wt(v,"FORBID_CONTENTS")&&pn(v.FORBID_CONTENTS)?gt({},v.FORBID_CONTENTS,$e):Le,Me=Wt(v,"FORBID_TAGS")&&pn(v.FORBID_TAGS)?gt({},v.FORBID_TAGS,$e):cn({}),fe=Wt(v,"FORBID_ATTR")&&pn(v.FORBID_ATTR)?gt({},v.FORBID_ATTR,$e):cn({}),ae=Wt(v,"USE_PROFILES")?v.USE_PROFILES&&typeof v.USE_PROFILES=="object"?cn(v.USE_PROFILES):v.USE_PROFILES:!1,ve=v.ALLOW_ARIA_ATTR!==!1,ye=v.ALLOW_DATA_ATTR!==!1,Ie=v.ALLOW_UNKNOWN_PROTOCOLS||!1,be=v.ALLOW_SELF_CLOSE_IN_ATTR!==!1,ke=v.SAFE_FOR_TEMPLATES||!1,xe=v.SAFE_FOR_XML!==!1,Ee=v.WHOLE_DOCUMENT||!1,Ne=v.RETURN_DOM||!1,Oe=v.RETURN_DOM_FRAGMENT||!1,J=v.RETURN_TRUSTED_TYPE||!1,De=v.FORCE_BODY||!1,We=v.SANITIZE_DOM!==!1,Fe=v.SANITIZE_NAMED_PROPS||!1,x=v.KEEP_CONTENT!==!1,Z=v.IN_PLACE||!1,K=r_(v.ALLOWED_URI_REGEXP)?v.ALLOWED_URI_REGEXP:fd,qe=typeof v.NAMESPACE=="string"?v.NAMESPACE:Ce,Be=Wt(v,"MATHML_TEXT_INTEGRATION_POINTS")&&v.MATHML_TEXT_INTEGRATION_POINTS&&typeof v.MATHML_TEXT_INTEGRATION_POINTS=="object"?cn(v.MATHML_TEXT_INTEGRATION_POINTS):gt({},["mi","mo","mn","ms","mtext"]),Te=Wt(v,"HTML_INTEGRATION_POINTS")&&v.HTML_INTEGRATION_POINTS&&typeof v.HTML_INTEGRATION_POINTS=="object"?cn(v.HTML_INTEGRATION_POINTS):gt({},["annotation-xml"]);const $=Wt(v,"CUSTOM_ELEMENT_HANDLING")&&v.CUSTOM_ELEMENT_HANDLING&&typeof v.CUSTOM_ELEMENT_HANDLING=="object"?cn(v.CUSTOM_ELEMENT_HANDLING):Qr(null);if(re=Qr(null),Wt($,"tagNameCheck")&&Mn($.tagNameCheck)&&(re.tagNameCheck=$.tagNameCheck),Wt($,"attributeNameCheck")&&Mn($.attributeNameCheck)&&(re.attributeNameCheck=$.attributeNameCheck),Wt($,"allowCustomizedBuiltInElements")&&typeof $.allowCustomizedBuiltInElements=="boolean"&&(re.allowCustomizedBuiltInElements=$.allowCustomizedBuiltInElements),ke&&(ye=!1),Oe&&(Ne=!0),ae&&(se=gt({},cd),N=Qr(null),ae.html===!0&&(gt(se,ld),gt(N,ud)),ae.svg===!0&&(gt(se,Do),gt(N,Oo),gt(N,ms)),ae.svgFilters===!0&&(gt(se,ko),gt(N,Oo),gt(N,ms)),ae.mathMl===!0&&(gt(se,Uo),gt(N,dd),gt(N,ms))),oe.tagCheck=null,oe.attributeCheck=null,Wt(v,"ADD_TAGS")&&(typeof v.ADD_TAGS=="function"?oe.tagCheck=v.ADD_TAGS:pn(v.ADD_TAGS)&&(se===ne&&(se=cn(se)),gt(se,v.ADD_TAGS,$e))),Wt(v,"ADD_ATTR")&&(typeof v.ADD_ATTR=="function"?oe.attributeCheck=v.ADD_ATTR:pn(v.ADD_ATTR)&&(N===V&&(N=cn(N)),gt(N,v.ADD_ATTR,$e))),Wt(v,"ADD_URI_SAFE_ATTR")&&pn(v.ADD_URI_SAFE_ATTR)&&gt(we,v.ADD_URI_SAFE_ATTR,$e),Wt(v,"FORBID_CONTENTS")&&pn(v.FORBID_CONTENTS)&&(de===Le&&(de=cn(de)),gt(de,v.FORBID_CONTENTS,$e)),Wt(v,"ADD_FORBID_CONTENTS")&&pn(v.ADD_FORBID_CONTENTS)&&(de===Le&&(de=cn(de)),gt(de,v.ADD_FORBID_CONTENTS,$e)),x&&(se["#text"]=!0),Ee&&gt(se,["html","head","body"]),se.table&&(gt(se,["tbody"]),delete Me.tbody),v.TRUSTED_TYPES_POLICY){if(typeof v.TRUSTED_TYPES_POLICY.createHTML!="function")throw ya('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');if(typeof v.TRUSTED_TYPES_POLICY.createScriptURL!="function")throw ya('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');R=v.TRUSTED_TYPES_POLICY,C=R.createHTML("")}else R===void 0&&(R=__(h,r)),R!==null&&typeof C=="string"&&(C=R.createHTML(""));(Q.uponSanitizeElement.length>0||Q.uponSanitizeAttribute.length>0)&&se===ne&&(se=cn(se)),Q.uponSanitizeAttribute.length>0&&N===V&&(N=cn(N)),vn&&vn(v),It=v},ls=gt({},[...Do,...ko,...a_]),cs=gt({},[...Uo,...s_]),us=function(v){let $=_(v);(!$||!$.tagName)&&($={namespaceURI:qe,tagName:"template"});const le=ka(v.tagName),pe=ka($.tagName);return st[v.namespaceURI]?v.namespaceURI===Pe?$.namespaceURI===Ce?le==="svg":$.namespaceURI===Je?le==="svg"&&(pe==="annotation-xml"||Be[pe]):!!ls[le]:v.namespaceURI===Je?$.namespaceURI===Ce?le==="math":$.namespaceURI===Pe?le==="math"&&Te[pe]:!!cs[le]:v.namespaceURI===Ce?$.namespaceURI===Pe&&!Te[pe]||$.namespaceURI===Je&&!Be[pe]?!1:!cs[le]&&(Ve[le]||!ls[le]):!!(Ye==="application/xhtml+xml"&&st[v.namespaceURI]):!1},hn=function(v){Lr(e.removed,{element:v});try{_(v).removeChild(v)}catch{m(v)}},xi=function(v,$){try{Lr(e.removed,{attribute:$.getAttributeNode(v),from:$})}catch{Lr(e.removed,{attribute:null,from:$})}if($.removeAttribute(v),v==="is")if(Ne||Oe)try{hn($)}catch{}else try{$.setAttribute(v,"")}catch{}},ma=function(v){let $=null,le=null;if(De)v="<remove></remove>"+v;else{const ze=rd(v,/^[\r\n\t ]+/);le=ze&&ze[0]}Ye==="application/xhtml+xml"&&qe===Ce&&(v='<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>'+v+"</body></html>");const pe=R?R.createHTML(v):v;if(qe===Ce)try{$=new f().parseFromString(pe,Ye)}catch{}if(!$||!$.documentElement){$=A.createDocument(qe,"template",null);try{$.documentElement.innerHTML=je?C:pe}catch{}}const he=$.body||$.documentElement;return v&&le&&he.insertBefore(t.createTextNode(le),he.childNodes[0]||null),qe===Ce?H.call($,Ee?"html":"body")[0]:Ee?$.documentElement:he},ga=function(v){return k.call(v.ownerDocument||v,v,c.SHOW_ELEMENT|c.SHOW_COMMENT|c.SHOW_TEXT|c.SHOW_PROCESSING_INSTRUCTION|c.SHOW_CDATA_SECTION,null)},Zn=function(v){v.normalize();const $=k.call(v.ownerDocument||v,v,c.SHOW_TEXT|c.SHOW_COMMENT|c.SHOW_CDATA_SECTION|c.SHOW_PROCESSING_INSTRUCTION,null);let le=$.nextNode();for(;le;){let pe=le.data;Pr([G,T,w],he=>{pe=Dr(pe,he," ")}),le.data=pe,le=$.nextNode()}},Oi=function(v){const $=B?B(v):null;return typeof $!="string"||$e($)!=="form"?!1:typeof v.nodeName!="string"||typeof v.textContent!="string"||typeof v.removeChild!="function"||v.attributes!==D(v)||typeof v.removeAttribute!="function"||typeof v.setAttribute!="function"||typeof v.namespaceURI!="string"||typeof v.insertBefore!="function"||typeof v.hasChildNodes!="function"||v.nodeType!==y(v)||v.childNodes!==g(v)},Fi=function(v){if(!y||typeof v!="object"||v===null)return!1;try{return y(v)===Qn.documentFragment}catch{return!1}},rr=function(v){if(!y||typeof v!="object"||v===null)return!1;try{return typeof y(v)=="number"}catch{return!1}};function bn(it,v,$){Pr(it,le=>{le.call(e,v,$,It)})}const _a=function(v){let $=null;if(bn(Q.beforeSanitizeElements,v,null),Oi(v))return hn(v),!0;const le=$e(v.nodeName);if(bn(Q.uponSanitizeElement,v,{tagName:le,allowedTags:se}),xe&&v.hasChildNodes()&&!rr(v.firstElementChild)&&rn(/<[/\w!]/g,v.innerHTML)&&rn(/<[/\w!]/g,v.textContent)||xe&&v.namespaceURI===Ce&&le==="style"&&rr(v.firstElementChild)||v.nodeType===Qn.progressingInstruction||xe&&v.nodeType===Qn.comment&&rn(/<[/\w]/g,v.data))return hn(v),!0;if(Me[le]||!(oe.tagCheck instanceof Function&&oe.tagCheck(le))&&!se[le]){if(!Me[le]&&va(le)&&(re.tagNameCheck instanceof RegExp&&rn(re.tagNameCheck,le)||re.tagNameCheck instanceof Function&&re.tagNameCheck(le)))return!1;if(x&&!de[le]){const he=_(v),ze=g(v);if(ze&&he){const Ke=ze.length;for(let Xe=Ke-1;Xe>=0;--Xe){const Qe=p(ze[Xe],!0);he.insertBefore(Qe,E(v))}}}return hn(v),!0}return(y?y(v):v.nodeType)===Qn.element&&!us(v)||(le==="noscript"||le==="noembed"||le==="noframes")&&rn(/<\/no(script|embed|frames)/i,v.innerHTML)?(hn(v),!0):(ke&&v.nodeType===Qn.text&&($=v.textContent,Pr([G,T,w],he=>{$=Dr($,he," ")}),v.textContent!==$&&(Lr(e.removed,{element:v.cloneNode()}),v.textContent=$)),bn(Q.afterSanitizeElements,v,null),!1)},ar=function(v,$,le){if(fe[$]||We&&($==="id"||$==="name")&&(le in t||le in yt))return!1;const pe=N[$]||oe.attributeCheck instanceof Function&&oe.attributeCheck($,v);if(!(ye&&!fe[$]&&rn(I,$))){if(!(ve&&rn(F,$))){if(!pe||fe[$]){if(!(va(v)&&(re.tagNameCheck instanceof RegExp&&rn(re.tagNameCheck,v)||re.tagNameCheck instanceof Function&&re.tagNameCheck(v))&&(re.attributeNameCheck instanceof RegExp&&rn(re.attributeNameCheck,$)||re.attributeNameCheck instanceof Function&&re.attributeNameCheck($,v))||$==="is"&&re.allowCustomizedBuiltInElements&&(re.tagNameCheck instanceof RegExp&&rn(re.tagNameCheck,le)||re.tagNameCheck instanceof Function&&re.tagNameCheck(le))))return!1}else if(!we[$]){if(!rn(K,Dr(le,te,""))){if(!(($==="src"||$==="xlink:href"||$==="href")&&v!=="script"&&ad(le,"data:")===0&&He[v])){if(!(Ie&&!rn(Y,Dr(le,te,"")))){if(le)return!1}}}}}}return!0},ds=gt({},["annotation-xml","color-profile","font-face","font-face-format","font-face-name","font-face-src","font-face-uri","missing-glyph"]),va=function(v){return!ds[ka(v)]&&rn(X,v)},fs=function(v){bn(Q.beforeSanitizeAttributes,v,null);const $=v.attributes;if(!$||Oi(v))return;const le={attrName:"",attrValue:"",keepAttr:!0,allowedAttributes:N,forceKeepAttr:void 0};let pe=$.length;for(;pe--;){const he=$[pe],ze=he.name,Ke=he.namespaceURI,Xe=he.value,Qe=$e(ze),rt=Xe;let at=ze==="value"?rt:Qg(rt);if(le.attrName=Qe,le.attrValue=at,le.keepAttr=!0,le.forceKeepAttr=void 0,bn(Q.uponSanitizeAttribute,v,le),at=le.attrValue,Fe&&(Qe==="id"||Qe==="name")&&ad(at,P)!==0&&(xi(ze,v),at=P+at),xe&&rn(/((--!?|])>)|<\/(style|script|title|xmp|textarea|noscript|iframe|noembed|noframes)/i,at)){xi(ze,v);continue}if(Qe==="attributename"&&rd(at,"href")){xi(ze,v);continue}if(le.forceKeepAttr)continue;if(!le.keepAttr){xi(ze,v);continue}if(!be&&rn(/\/>/i,at)){xi(ze,v);continue}ke&&Pr([G,T,w],ot=>{at=Dr(at,ot," ")});const pt=$e(v.nodeName);if(!ar(pt,Qe,at)){xi(ze,v);continue}if(R&&typeof h=="object"&&typeof h.getAttributeType=="function"&&!Ke)switch(h.getAttributeType(pt,Qe)){case"TrustedHTML":{at=R.createHTML(at);break}case"TrustedScriptURL":{at=R.createScriptURL(at);break}}if(at!==rt)try{Ke?v.setAttributeNS(Ke,ze,at):v.setAttribute(ze,at),Oi(v)?hn(v):id(e.removed)}catch{xi(ze,v)}}bn(Q.afterSanitizeAttributes,v,null)},Rr=function(v){let $=null;const le=ga(v);for(bn(Q.beforeSanitizeShadowDOM,v,null);$=le.nextNode();)if(bn(Q.uponSanitizeShadowNode,$,null),_a($),fs($),Fi($.content)&&Rr($.content),(y?y($):$.nodeType)===Qn.element){const he=O?O($):$.shadowRoot;Fi(he)&&(Bi(he),Rr(he))}bn(Q.afterSanitizeShadowDOM,v,null)},Bi=function(v){const $=y?y(v):v.nodeType;if($===Qn.element){const he=O?O(v):v.shadowRoot;Fi(he)&&(Bi(he),Rr(he))}const le=g?g(v):v.childNodes;if(!le)return;const pe=[];Pr(le,he=>{Lr(pe,he)});for(const he of pe)Bi(he);if($===Qn.element){const he=B?B(v):null;if(typeof he=="string"&&$e(he)==="template"){const ze=v.content;Fi(ze)&&Bi(ze)}}};return e.sanitize=function(it){let v=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},$=null,le=null,pe=null,he=null;if(je=!it,je&&(it="<!-->"),typeof it!="string"&&!rr(it)&&(it=i_(it),typeof it!="string"))throw ya("dirty is not a string, aborting");if(!e.isSupported)return it;if(_e||xn(v),e.removed=[],typeof it=="string"&&(Z=!1),Z){const Xe=B?B(it):it.nodeName;if(typeof Xe=="string"){const Qe=$e(Xe);if(!se[Qe]||Me[Qe])throw ya("root node is forbidden and cannot be sanitized in-place")}if(Oi(it))throw ya("root node is clobbered and cannot be sanitized in-place");Bi(it)}else if(rr(it))$=ma("<!---->"),le=$.ownerDocument.importNode(it,!0),le.nodeType===Qn.element&&le.nodeName==="BODY"||le.nodeName==="HTML"?$=le:$.appendChild(le),Bi(le);else{if(!Ne&&!ke&&!Ee&&it.indexOf("<")===-1)return R&&J?R.createHTML(it):it;if($=ma(it),!$)return Ne?null:J?C:""}$&&De&&hn($.firstChild);const ze=ga(Z?it:$);for(;pe=ze.nextNode();)_a(pe),fs(pe),Fi(pe.content)&&Rr(pe.content);if(Z)return ke&&Zn(it),it;if(Ne){if(ke&&Zn($),Oe)for(he=z.call($.ownerDocument);$.firstChild;)he.appendChild($.firstChild);else he=$;return(N.shadowroot||N.shadowrootmode)&&(he=q.call(i,he,!0)),he}let Ke=Ee?$.outerHTML:$.innerHTML;return Ee&&se["!doctype"]&&$.ownerDocument&&$.ownerDocument.doctype&&$.ownerDocument.doctype.name&&rn(p_,$.ownerDocument.doctype.name)&&(Ke="<!DOCTYPE "+$.ownerDocument.doctype.name+`>
`+Ke),ke&&Pr([G,T,w],Xe=>{Ke=Dr(Ke,Xe," ")}),R&&J?R.createHTML(Ke):Ke},e.setConfig=function(){let it=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};xn(it),_e=!0},e.clearConfig=function(){It=null,_e=!1},e.isValidAttribute=function(it,v,$){It||xn({});const le=$e(it),pe=$e(v);return ar(le,pe,$)},e.addHook=function(it,v){typeof v=="function"&&Lr(Q[it],v)},e.removeHook=function(it,v){if(v!==void 0){const $=Zg(Q[it],v);return $===-1?void 0:Jg(Q[it],$,1)[0]}return id(Q[it])},e.removeHooks=function(it){Q[it]=[]},e.removeAllHooks=function(){Q=hd()},e}var v_=mh();function x_(n){return n&&n.__esModule&&Object.prototype.hasOwnProperty.call(n,"default")?n.default:n}function gh(n){return n instanceof Map?n.clear=n.delete=n.set=function(){throw new Error("map is read-only")}:n instanceof Set&&(n.add=n.clear=n.delete=function(){throw new Error("set is read-only")}),Object.freeze(n),Object.getOwnPropertyNames(n).forEach(e=>{const t=n[e],i=typeof t;(i==="object"||i==="function")&&!Object.isFrozen(t)&&gh(t)}),n}let pd=class{constructor(e){e.data===void 0&&(e.data={}),this.data=e.data,this.isMatchIgnored=!1}ignoreMatch(){this.isMatchIgnored=!0}};function _h(n){return n.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#x27;")}function Qi(n,...e){const t=Object.create(null);for(const i in n)t[i]=n[i];return e.forEach(function(i){for(const r in i)t[r]=i[r]}),t}const b_="</span>",md=n=>!!n.scope,S_=(n,{prefix:e})=>{if(n.startsWith("language:"))return n.replace("language:","language-");if(n.includes(".")){const t=n.split(".");return[`${e}${t.shift()}`,...t.map((i,r)=>`${i}${"_".repeat(r+1)}`)].join(" ")}return`${e}${n}`};class y_{constructor(e,t){this.buffer="",this.classPrefix=t.classPrefix,e.walk(this)}addText(e){this.buffer+=_h(e)}openNode(e){if(!md(e))return;const t=S_(e.scope,{prefix:this.classPrefix});this.span(t)}closeNode(e){md(e)&&(this.buffer+=b_)}value(){return this.buffer}span(e){this.buffer+=`<span class="${e}">`}}const gd=(n={})=>{const e={children:[]};return Object.assign(e,n),e};class Lc{constructor(){this.rootNode=gd(),this.stack=[this.rootNode]}get top(){return this.stack[this.stack.length-1]}get root(){return this.rootNode}add(e){this.top.children.push(e)}openNode(e){const t=gd({scope:e});this.add(t),this.stack.push(t)}closeNode(){if(this.stack.length>1)return this.stack.pop()}closeAllNodes(){for(;this.closeNode(););}toJSON(){return JSON.stringify(this.rootNode,null,4)}walk(e){return this.constructor._walk(e,this.rootNode)}static _walk(e,t){return typeof t=="string"?e.addText(t):t.children&&(e.openNode(t),t.children.forEach(i=>this._walk(e,i)),e.closeNode(t)),e}static _collapse(e){typeof e!="string"&&e.children&&(e.children.every(t=>typeof t=="string")?e.children=[e.children.join("")]:e.children.forEach(t=>{Lc._collapse(t)}))}}class E_ extends Lc{constructor(e){super(),this.options=e}addText(e){e!==""&&this.add(e)}startScope(e){this.openNode(e)}endScope(){this.closeNode()}__addSublanguage(e,t){const i=e.root;t&&(i.scope=`language:${t}`),this.add(i)}toHTML(){return new y_(this,this.options).value()}finalize(){return this.closeAllNodes(),!0}}function Ya(n){return n?typeof n=="string"?n:n.source:null}function vh(n){return Tr("(?=",n,")")}function M_(n){return Tr("(?:",n,")*")}function T_(n){return Tr("(?:",n,")?")}function Tr(...n){return n.map(t=>Ya(t)).join("")}function w_(n){const e=n[n.length-1];return typeof e=="object"&&e.constructor===Object?(n.splice(n.length-1,1),e):{}}function Dc(...n){return"("+(w_(n).capture?"":"?:")+n.map(i=>Ya(i)).join("|")+")"}function xh(n){return new RegExp(n.toString()+"|").exec("").length-1}function A_(n,e){const t=n&&n.exec(e);return t&&t.index===0}const R_=/\[(?:[^\\\]]|\\.)*\]|\(\??|\\([1-9][0-9]*)|\\./;function kc(n,{joinWith:e}){let t=0;return n.map(i=>{t+=1;const r=t;let a=Ya(i),o="";for(;a.length>0;){const l=R_.exec(a);if(!l){o+=a;break}o+=a.substring(0,l.index),a=a.substring(l.index+l[0].length),l[0][0]==="\\"&&l[1]?o+="\\"+String(Number(l[1])+r):(o+=l[0],l[0]==="("&&t++)}return o}).map(i=>`(${i})`).join(e)}const C_=/\b\B/,bh="[a-zA-Z]\\w*",Uc="[a-zA-Z_]\\w*",Sh="\\b\\d+(\\.\\d+)?",yh="(-?)(\\b0[xX][a-fA-F0-9]+|(\\b\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)",Eh="\\b(0b[01]+)",I_="!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|-|-=|/=|/|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~",N_=(n={})=>{const e=/^#![ ]*\//;return n.binary&&(n.begin=Tr(e,/.*\b/,n.binary,/\b.*/)),Qi({scope:"meta",begin:e,end:/$/,relevance:0,"on:begin":(t,i)=>{t.index!==0&&i.ignoreMatch()}},n)},Ka={begin:"\\\\[\\s\\S]",relevance:0},P_={scope:"string",begin:"'",end:"'",illegal:"\\n",contains:[Ka]},L_={scope:"string",begin:'"',end:'"',illegal:"\\n",contains:[Ka]},D_={begin:/\b(a|an|the|are|I'm|isn't|don't|doesn't|won't|but|just|should|pretty|simply|enough|gonna|going|wtf|so|such|will|you|your|they|like|more)\b/},_o=function(n,e,t={}){const i=Qi({scope:"comment",begin:n,end:e,contains:[]},t);i.contains.push({scope:"doctag",begin:"[ ]*(?=(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):)",end:/(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):/,excludeBegin:!0,relevance:0});const r=Dc("I","a","is","so","us","to","at","if","in","it","on",/[A-Za-z]+['](d|ve|re|ll|t|s|n)/,/[A-Za-z]+[-][a-z]+/,/[A-Za-z][a-z]{2,}/);return i.contains.push({begin:Tr(/[ ]+/,"(",r,/[.]?[:]?([.][ ]|[ ])/,"){3}")}),i},k_=_o("//","$"),U_=_o("/\\*","\\*/"),O_=_o("#","$"),F_={scope:"number",begin:Sh,relevance:0},B_={scope:"number",begin:yh,relevance:0},z_={scope:"number",begin:Eh,relevance:0},H_={scope:"regexp",begin:/\/(?=[^/\n]*\/)/,end:/\/[gimuy]*/,contains:[Ka,{begin:/\[/,end:/\]/,relevance:0,contains:[Ka]}]},G_={scope:"title",begin:bh,relevance:0},V_={scope:"title",begin:Uc,relevance:0},W_={begin:"\\.\\s*"+Uc,relevance:0},$_=function(n){return Object.assign(n,{"on:begin":(e,t)=>{t.data._beginMatch=e[1]},"on:end":(e,t)=>{t.data._beginMatch!==e[1]&&t.ignoreMatch()}})};var gs=Object.freeze({__proto__:null,APOS_STRING_MODE:P_,BACKSLASH_ESCAPE:Ka,BINARY_NUMBER_MODE:z_,BINARY_NUMBER_RE:Eh,COMMENT:_o,C_BLOCK_COMMENT_MODE:U_,C_LINE_COMMENT_MODE:k_,C_NUMBER_MODE:B_,C_NUMBER_RE:yh,END_SAME_AS_BEGIN:$_,HASH_COMMENT_MODE:O_,IDENT_RE:bh,MATCH_NOTHING_RE:C_,METHOD_GUARD:W_,NUMBER_MODE:F_,NUMBER_RE:Sh,PHRASAL_WORDS_MODE:D_,QUOTE_STRING_MODE:L_,REGEXP_MODE:H_,RE_STARTERS_RE:I_,SHEBANG:N_,TITLE_MODE:G_,UNDERSCORE_IDENT_RE:Uc,UNDERSCORE_TITLE_MODE:V_});function X_(n,e){n.input[n.index-1]==="."&&e.ignoreMatch()}function q_(n,e){n.className!==void 0&&(n.scope=n.className,delete n.className)}function Y_(n,e){e&&n.beginKeywords&&(n.begin="\\b("+n.beginKeywords.split(" ").join("|")+")(?!\\.)(?=\\b|\\s)",n.__beforeBegin=X_,n.keywords=n.keywords||n.beginKeywords,delete n.beginKeywords,n.relevance===void 0&&(n.relevance=0))}function K_(n,e){Array.isArray(n.illegal)&&(n.illegal=Dc(...n.illegal))}function Z_(n,e){if(n.match){if(n.begin||n.end)throw new Error("begin & end are not supported with match");n.begin=n.match,delete n.match}}function J_(n,e){n.relevance===void 0&&(n.relevance=1)}const Q_=(n,e)=>{if(!n.beforeMatch)return;if(n.starts)throw new Error("beforeMatch cannot be used with starts");const t=Object.assign({},n);Object.keys(n).forEach(i=>{delete n[i]}),n.keywords=t.keywords,n.begin=Tr(t.beforeMatch,vh(t.begin)),n.starts={relevance:0,contains:[Object.assign(t,{endsParent:!0})]},n.relevance=0,delete t.beforeMatch},j_=["of","and","for","in","not","or","if","then","parent","list","value"],ev="keyword";function Mh(n,e,t=ev){const i=Object.create(null);return typeof n=="string"?r(t,n.split(" ")):Array.isArray(n)?r(t,n):Object.keys(n).forEach(function(a){Object.assign(i,Mh(n[a],e,a))}),i;function r(a,o){e&&(o=o.map(l=>l.toLowerCase())),o.forEach(function(l){const c=l.split("|");i[c[0]]=[a,tv(c[0],c[1])]})}}function tv(n,e){return e?Number(e):nv(n)?0:1}function nv(n){return j_.includes(n.toLowerCase())}const _d={},_r=n=>{console.error(n)},vd=(n,...e)=>{console.log(`WARN: ${n}`,...e)},kr=(n,e)=>{_d[`${n}/${e}`]||(console.log(`Deprecated as of ${n}. ${e}`),_d[`${n}/${e}`]=!0)},eo=new Error;function Th(n,e,{key:t}){let i=0;const r=n[t],a={},o={};for(let l=1;l<=e.length;l++)o[l+i]=r[l],a[l+i]=!0,i+=xh(e[l-1]);n[t]=o,n[t]._emit=a,n[t]._multi=!0}function iv(n){if(Array.isArray(n.begin)){if(n.skip||n.excludeBegin||n.returnBegin)throw _r("skip, excludeBegin, returnBegin not compatible with beginScope: {}"),eo;if(typeof n.beginScope!="object"||n.beginScope===null)throw _r("beginScope must be object"),eo;Th(n,n.begin,{key:"beginScope"}),n.begin=kc(n.begin,{joinWith:""})}}function rv(n){if(Array.isArray(n.end)){if(n.skip||n.excludeEnd||n.returnEnd)throw _r("skip, excludeEnd, returnEnd not compatible with endScope: {}"),eo;if(typeof n.endScope!="object"||n.endScope===null)throw _r("endScope must be object"),eo;Th(n,n.end,{key:"endScope"}),n.end=kc(n.end,{joinWith:""})}}function av(n){n.scope&&typeof n.scope=="object"&&n.scope!==null&&(n.beginScope=n.scope,delete n.scope)}function sv(n){av(n),typeof n.beginScope=="string"&&(n.beginScope={_wrap:n.beginScope}),typeof n.endScope=="string"&&(n.endScope={_wrap:n.endScope}),iv(n),rv(n)}function ov(n){function e(o,l){return new RegExp(Ya(o),"m"+(n.case_insensitive?"i":"")+(n.unicodeRegex?"u":"")+(l?"g":""))}class t{constructor(){this.matchIndexes={},this.regexes=[],this.matchAt=1,this.position=0}addRule(l,c){c.position=this.position++,this.matchIndexes[this.matchAt]=c,this.regexes.push([c,l]),this.matchAt+=xh(l)+1}compile(){this.regexes.length===0&&(this.exec=()=>null);const l=this.regexes.map(c=>c[1]);this.matcherRe=e(kc(l,{joinWith:"|"}),!0),this.lastIndex=0}exec(l){this.matcherRe.lastIndex=this.lastIndex;const c=this.matcherRe.exec(l);if(!c)return null;const u=c.findIndex((h,d)=>d>0&&h!==void 0),f=this.matchIndexes[u];return c.splice(0,u),Object.assign(c,f)}}class i{constructor(){this.rules=[],this.multiRegexes=[],this.count=0,this.lastIndex=0,this.regexIndex=0}getMatcher(l){if(this.multiRegexes[l])return this.multiRegexes[l];const c=new t;return this.rules.slice(l).forEach(([u,f])=>c.addRule(u,f)),c.compile(),this.multiRegexes[l]=c,c}resumingScanAtSamePosition(){return this.regexIndex!==0}considerAll(){this.regexIndex=0}addRule(l,c){this.rules.push([l,c]),c.type==="begin"&&this.count++}exec(l){const c=this.getMatcher(this.regexIndex);c.lastIndex=this.lastIndex;let u=c.exec(l);if(this.resumingScanAtSamePosition()&&!(u&&u.index===this.lastIndex)){const f=this.getMatcher(0);f.lastIndex=this.lastIndex+1,u=f.exec(l)}return u&&(this.regexIndex+=u.position+1,this.regexIndex===this.count&&this.considerAll()),u}}function r(o){const l=new i;return o.contains.forEach(c=>l.addRule(c.begin,{rule:c,type:"begin"})),o.terminatorEnd&&l.addRule(o.terminatorEnd,{type:"end"}),o.illegal&&l.addRule(o.illegal,{type:"illegal"}),l}function a(o,l){const c=o;if(o.isCompiled)return c;[q_,Z_,sv,Q_].forEach(f=>f(o,l)),n.compilerExtensions.forEach(f=>f(o,l)),o.__beforeBegin=null,[Y_,K_,J_].forEach(f=>f(o,l)),o.isCompiled=!0;let u=null;return typeof o.keywords=="object"&&o.keywords.$pattern&&(o.keywords=Object.assign({},o.keywords),u=o.keywords.$pattern,delete o.keywords.$pattern),u=u||/\w+/,o.keywords&&(o.keywords=Mh(o.keywords,n.case_insensitive)),c.keywordPatternRe=e(u,!0),l&&(o.begin||(o.begin=/\B|\b/),c.beginRe=e(c.begin),!o.end&&!o.endsWithParent&&(o.end=/\B|\b/),o.end&&(c.endRe=e(c.end)),c.terminatorEnd=Ya(c.end)||"",o.endsWithParent&&l.terminatorEnd&&(c.terminatorEnd+=(o.end?"|":"")+l.terminatorEnd)),o.illegal&&(c.illegalRe=e(o.illegal)),o.contains||(o.contains=[]),o.contains=[].concat(...o.contains.map(function(f){return lv(f==="self"?o:f)})),o.contains.forEach(function(f){a(f,c)}),o.starts&&a(o.starts,l),c.matcher=r(c),c}if(n.compilerExtensions||(n.compilerExtensions=[]),n.contains&&n.contains.includes("self"))throw new Error("ERR: contains `self` is not supported at the top-level of a language.  See documentation.");return n.classNameAliases=Qi(n.classNameAliases||{}),a(n)}function wh(n){return n?n.endsWithParent||wh(n.starts):!1}function lv(n){return n.variants&&!n.cachedVariants&&(n.cachedVariants=n.variants.map(function(e){return Qi(n,{variants:null},e)})),n.cachedVariants?n.cachedVariants:wh(n)?Qi(n,{starts:n.starts?Qi(n.starts):null}):Object.isFrozen(n)?Qi(n):n}var cv="11.11.1";class uv extends Error{constructor(e,t){super(e),this.name="HTMLInjectionError",this.html=t}}const Fo=_h,xd=Qi,bd=Symbol("nomatch"),dv=7,Ah=function(n){const e=Object.create(null),t=Object.create(null),i=[];let r=!0;const a="Could not find the language '{}', did you forget to load/include a language module?",o={disableAutodetect:!0,name:"Plain text",contains:[]};let l={ignoreUnescapedHTML:!1,throwUnescapedHTML:!1,noHighlightRe:/^(no-?highlight)$/i,languageDetectRe:/\blang(?:uage)?-([\w-]+)\b/i,classPrefix:"hljs-",cssSelector:"pre code",languages:null,__emitter:E_};function c(T){return l.noHighlightRe.test(T)}function u(T){let w=T.className+" ";w+=T.parentNode?T.parentNode.className:"";const I=l.languageDetectRe.exec(w);if(I){const F=b(I[1]);return F||(vd(a.replace("{}",I[1])),vd("Falling back to no-highlight mode for this block.",T)),F?I[1]:"no-highlight"}return w.split(/\s+/).find(F=>c(F)||b(F))}function f(T,w,I){let F="",Y="";typeof w=="object"?(F=T,I=w.ignoreIllegals,Y=w.language):(kr("10.7.0","highlight(lang, code, ...args) has been deprecated."),kr("10.7.0",`Please use highlight(code, options) instead.
https://github.com/highlightjs/highlight.js/issues/2277`),Y=T,F=w),I===void 0&&(I=!0);const te={code:F,language:Y};Q("before:highlight",te);const X=te.result?te.result:h(te.language,te.code,I);return X.code=te.code,Q("after:highlight",X),X}function h(T,w,I,F){const Y=Object.create(null);function te(P,x){return P.keywords[x]}function X(){if(!Ee.keywords){De.addText(Ne);return}let P=0;Ee.keywordPatternRe.lastIndex=0;let x=Ee.keywordPatternRe.exec(Ne),Z="";for(;x;){Z+=Ne.substring(P,x.index);const ae=be.case_insensitive?x[0].toLowerCase():x[0],de=te(Ee,ae);if(de){const[Le,He]=de;if(De.addText(Z),Z="",Y[ae]=(Y[ae]||0)+1,Y[ae]<=dv&&(Oe+=He),Le.startsWith("_"))Z+=x[0];else{const Se=be.classNameAliases[Le]||Le;ne(x[0],Se)}}else Z+=x[0];P=Ee.keywordPatternRe.lastIndex,x=Ee.keywordPatternRe.exec(Ne)}Z+=Ne.substring(P),De.addText(Z)}function K(){if(Ne==="")return;let P=null;if(typeof Ee.subLanguage=="string"){if(!e[Ee.subLanguage]){De.addText(Ne);return}P=h(Ee.subLanguage,Ne,!0,_e[Ee.subLanguage]),_e[Ee.subLanguage]=P._top}else P=p(Ne,Ee.subLanguage.length?Ee.subLanguage:null);Ee.relevance>0&&(Oe+=P.relevance),De.__addSublanguage(P._emitter,P.language)}function se(){Ee.subLanguage!=null?K():X(),Ne=""}function ne(P,x){P!==""&&(De.startScope(x),De.addText(P),De.endScope())}function N(P,x){let Z=1;const ae=x.length-1;for(;Z<=ae;){if(!P._emit[Z]){Z++;continue}const de=be.classNameAliases[P[Z]]||P[Z],Le=x[Z];de?ne(Le,de):(Ne=Le,X(),Ne=""),Z++}}function V(P,x){return P.scope&&typeof P.scope=="string"&&De.openNode(be.classNameAliases[P.scope]||P.scope),P.beginScope&&(P.beginScope._wrap?(ne(Ne,be.classNameAliases[P.beginScope._wrap]||P.beginScope._wrap),Ne=""):P.beginScope._multi&&(N(P.beginScope,x),Ne="")),Ee=Object.create(P,{parent:{value:Ee}}),Ee}function re(P,x,Z){let ae=A_(P.endRe,Z);if(ae){if(P["on:end"]){const de=new pd(P);P["on:end"](x,de),de.isMatchIgnored&&(ae=!1)}if(ae){for(;P.endsParent&&P.parent;)P=P.parent;return P}}if(P.endsWithParent)return re(P.parent,x,Z)}function Me(P){return Ee.matcher.regexIndex===0?(Ne+=P[0],1):(Fe=!0,0)}function fe(P){const x=P[0],Z=P.rule,ae=new pd(Z),de=[Z.__beforeBegin,Z["on:begin"]];for(const Le of de)if(Le&&(Le(P,ae),ae.isMatchIgnored))return Me(x);return Z.skip?Ne+=x:(Z.excludeBegin&&(Ne+=x),se(),!Z.returnBegin&&!Z.excludeBegin&&(Ne=x)),V(Z,P),Z.returnBegin?0:x.length}function oe(P){const x=P[0],Z=w.substring(P.index),ae=re(Ee,P,Z);if(!ae)return bd;const de=Ee;Ee.endScope&&Ee.endScope._wrap?(se(),ne(x,Ee.endScope._wrap)):Ee.endScope&&Ee.endScope._multi?(se(),N(Ee.endScope,P)):de.skip?Ne+=x:(de.returnEnd||de.excludeEnd||(Ne+=x),se(),de.excludeEnd&&(Ne=x));do Ee.scope&&De.closeNode(),!Ee.skip&&!Ee.subLanguage&&(Oe+=Ee.relevance),Ee=Ee.parent;while(Ee!==ae.parent);return ae.starts&&V(ae.starts,P),de.returnEnd?0:x.length}function ve(){const P=[];for(let x=Ee;x!==be;x=x.parent)x.scope&&P.unshift(x.scope);P.forEach(x=>De.openNode(x))}let ye={};function Ie(P,x){const Z=x&&x[0];if(Ne+=P,Z==null)return se(),0;if(ye.type==="begin"&&x.type==="end"&&ye.index===x.index&&Z===""){if(Ne+=w.slice(x.index,x.index+1),!r){const ae=new Error(`0 width match regex (${T})`);throw ae.languageName=T,ae.badRule=ye.rule,ae}return 1}if(ye=x,x.type==="begin")return fe(x);if(x.type==="illegal"&&!I){const ae=new Error('Illegal lexeme "'+Z+'" for mode "'+(Ee.scope||"<unnamed>")+'"');throw ae.mode=Ee,ae}else if(x.type==="end"){const ae=oe(x);if(ae!==bd)return ae}if(x.type==="illegal"&&Z==="")return Ne+=`
`,1;if(We>1e5&&We>x.index*3)throw new Error("potential infinite loop, way more iterations than matches");return Ne+=Z,Z.length}const be=b(T);if(!be)throw _r(a.replace("{}",T)),new Error('Unknown language: "'+T+'"');const ke=ov(be);let xe="",Ee=F||ke;const _e={},De=new l.__emitter(l);ve();let Ne="",Oe=0,J=0,We=0,Fe=!1;try{if(be.__emitTokens)be.__emitTokens(w,De);else{for(Ee.matcher.considerAll();;){We++,Fe?Fe=!1:Ee.matcher.considerAll(),Ee.matcher.lastIndex=J;const P=Ee.matcher.exec(w);if(!P)break;const x=w.substring(J,P.index),Z=Ie(x,P);J=P.index+Z}Ie(w.substring(J))}return De.finalize(),xe=De.toHTML(),{language:T,value:xe,relevance:Oe,illegal:!1,_emitter:De,_top:Ee}}catch(P){if(P.message&&P.message.includes("Illegal"))return{language:T,value:Fo(w),illegal:!0,relevance:0,_illegalBy:{message:P.message,index:J,context:w.slice(J-100,J+100),mode:P.mode,resultSoFar:xe},_emitter:De};if(r)return{language:T,value:Fo(w),illegal:!1,relevance:0,errorRaised:P,_emitter:De,_top:Ee};throw P}}function d(T){const w={value:Fo(T),illegal:!1,relevance:0,_top:o,_emitter:new l.__emitter(l)};return w._emitter.addText(T),w}function p(T,w){w=w||l.languages||Object.keys(e);const I=d(T),F=w.filter(b).filter(k).map(se=>h(se,T,!1));F.unshift(I);const Y=F.sort((se,ne)=>{if(se.relevance!==ne.relevance)return ne.relevance-se.relevance;if(se.language&&ne.language){if(b(se.language).supersetOf===ne.language)return 1;if(b(ne.language).supersetOf===se.language)return-1}return 0}),[te,X]=Y,K=te;return K.secondBest=X,K}function m(T,w,I){const F=w&&t[w]||I;T.classList.add("hljs"),T.classList.add(`language-${F}`)}function E(T){let w=null;const I=u(T);if(c(I))return;if(Q("before:highlightElement",{el:T,language:I}),T.dataset.highlighted){console.log("Element previously highlighted. To highlight again, first unset `dataset.highlighted`.",T);return}if(T.children.length>0&&(l.ignoreUnescapedHTML||(console.warn("One of your code blocks includes unescaped HTML. This is a potentially serious security risk."),console.warn("https://github.com/highlightjs/highlight.js/wiki/security"),console.warn("The element with unescaped HTML:"),console.warn(T)),l.throwUnescapedHTML))throw new uv("One of your code blocks includes unescaped HTML.",T.innerHTML);w=T;const F=w.textContent,Y=I?f(F,{language:I,ignoreIllegals:!0}):p(F);T.innerHTML=Y.value,T.dataset.highlighted="yes",m(T,I,Y.language),T.result={language:Y.language,re:Y.relevance,relevance:Y.relevance},Y.secondBest&&(T.secondBest={language:Y.secondBest.language,relevance:Y.secondBest.relevance}),Q("after:highlightElement",{el:T,result:Y,text:F})}function g(T){l=xd(l,T)}const _=()=>{y(),kr("10.6.0","initHighlighting() deprecated.  Use highlightAll() now.")};function O(){y(),kr("10.6.0","initHighlightingOnLoad() deprecated.  Use highlightAll() now.")}let D=!1;function y(){function T(){y()}if(document.readyState==="loading"){D||window.addEventListener("DOMContentLoaded",T,!1),D=!0;return}document.querySelectorAll(l.cssSelector).forEach(E)}function B(T,w){let I=null;try{I=w(n)}catch(F){if(_r("Language definition for '{}' could not be registered.".replace("{}",T)),r)_r(F);else throw F;I=o}I.name||(I.name=T),e[T]=I,I.rawDefinition=w.bind(null,n),I.aliases&&A(I.aliases,{languageName:T})}function R(T){delete e[T];for(const w of Object.keys(t))t[w]===T&&delete t[w]}function C(){return Object.keys(e)}function b(T){return T=(T||"").toLowerCase(),e[T]||e[t[T]]}function A(T,{languageName:w}){typeof T=="string"&&(T=[T]),T.forEach(I=>{t[I.toLowerCase()]=w})}function k(T){const w=b(T);return w&&!w.disableAutodetect}function z(T){T["before:highlightBlock"]&&!T["before:highlightElement"]&&(T["before:highlightElement"]=w=>{T["before:highlightBlock"](Object.assign({block:w.el},w))}),T["after:highlightBlock"]&&!T["after:highlightElement"]&&(T["after:highlightElement"]=w=>{T["after:highlightBlock"](Object.assign({block:w.el},w))})}function H(T){z(T),i.push(T)}function q(T){const w=i.indexOf(T);w!==-1&&i.splice(w,1)}function Q(T,w){const I=T;i.forEach(function(F){F[I]&&F[I](w)})}function G(T){return kr("10.7.0","highlightBlock will be removed entirely in v12.0"),kr("10.7.0","Please use highlightElement now."),E(T)}Object.assign(n,{highlight:f,highlightAuto:p,highlightAll:y,highlightElement:E,highlightBlock:G,configure:g,initHighlighting:_,initHighlightingOnLoad:O,registerLanguage:B,unregisterLanguage:R,listLanguages:C,getLanguage:b,registerAliases:A,autoDetection:k,inherit:xd,addPlugin:H,removePlugin:q}),n.debugMode=function(){r=!1},n.safeMode=function(){r=!0},n.versionString=cv,n.regex={concat:Tr,lookahead:vh,either:Dc,optional:T_,anyNumberOfTimes:M_};for(const T in gs)typeof gs[T]=="object"&&gh(gs[T]);return Object.assign(n,gs),n},aa=Ah({});aa.newInstance=()=>Ah({});var fv=aa;aa.HighlightJS=aa;aa.default=aa;const Ft=x_(fv);function hv(n){const e=n.regex,t={},i={begin:/\$\{/,end:/\}/,contains:["self",{begin:/:-/,contains:[t]}]};Object.assign(t,{className:"variable",variants:[{begin:e.concat(/\$[\w\d#@][\w\d_]*/,"(?![\\w\\d])(?![$])")},i]});const r={className:"subst",begin:/\$\(/,end:/\)/,contains:[n.BACKSLASH_ESCAPE]},a=n.inherit(n.COMMENT(),{match:[/(^|\s)/,/#.*$/],scope:{2:"comment"}}),o={begin:/<<-?\s*(?=\w+)/,starts:{contains:[n.END_SAME_AS_BEGIN({begin:/(\w+)/,end:/(\w+)/,className:"string"})]}},l={className:"string",begin:/"/,end:/"/,contains:[n.BACKSLASH_ESCAPE,t,r]};r.contains.push(l);const c={match:/\\"/},u={className:"string",begin:/'/,end:/'/},f={match:/\\'/},h={begin:/\$?\(\(/,end:/\)\)/,contains:[{begin:/\d+#[0-9a-f]+/,className:"number"},n.NUMBER_MODE,t]},d=["fish","bash","zsh","sh","csh","ksh","tcsh","dash","scsh"],p=n.SHEBANG({binary:`(${d.join("|")})`,relevance:10}),m={className:"function",begin:/\w[\w\d_]*\s*\(\s*\)\s*\{/,returnBegin:!0,contains:[n.inherit(n.TITLE_MODE,{begin:/\w[\w\d_]*/})],relevance:0},E=["if","then","else","elif","fi","time","for","while","until","in","do","done","case","esac","coproc","function","select"],g=["true","false"],_={match:/(\/[a-z._-]+)+/},O=["break","cd","continue","eval","exec","exit","export","getopts","hash","pwd","readonly","return","shift","test","times","trap","umask","unset"],D=["alias","bind","builtin","caller","command","declare","echo","enable","help","let","local","logout","mapfile","printf","read","readarray","source","sudo","type","typeset","ulimit","unalias"],y=["autoload","bg","bindkey","bye","cap","chdir","clone","comparguments","compcall","compctl","compdescribe","compfiles","compgroups","compquote","comptags","comptry","compvalues","dirs","disable","disown","echotc","echoti","emulate","fc","fg","float","functions","getcap","getln","history","integer","jobs","kill","limit","log","noglob","popd","print","pushd","pushln","rehash","sched","setcap","setopt","stat","suspend","ttyctl","unfunction","unhash","unlimit","unsetopt","vared","wait","whence","where","which","zcompile","zformat","zftp","zle","zmodload","zparseopts","zprof","zpty","zregexparse","zsocket","zstyle","ztcp"],B=["chcon","chgrp","chown","chmod","cp","dd","df","dir","dircolors","ln","ls","mkdir","mkfifo","mknod","mktemp","mv","realpath","rm","rmdir","shred","sync","touch","truncate","vdir","b2sum","base32","base64","cat","cksum","comm","csplit","cut","expand","fmt","fold","head","join","md5sum","nl","numfmt","od","paste","ptx","pr","sha1sum","sha224sum","sha256sum","sha384sum","sha512sum","shuf","sort","split","sum","tac","tail","tr","tsort","unexpand","uniq","wc","arch","basename","chroot","date","dirname","du","echo","env","expr","factor","groups","hostid","id","link","logname","nice","nohup","nproc","pathchk","pinky","printenv","printf","pwd","readlink","runcon","seq","sleep","stat","stdbuf","stty","tee","test","timeout","tty","uname","unlink","uptime","users","who","whoami","yes"];return{name:"Bash",aliases:["sh","zsh"],keywords:{$pattern:/\b[a-z][a-z0-9._-]+\b/,keyword:E,literal:g,built_in:[...O,...D,"set","shopt",...y,...B]},contains:[p,n.SHEBANG(),m,h,a,o,_,l,c,u,f,t]}}const pv=n=>({IMPORTANT:{scope:"meta",begin:"!important"},BLOCK_COMMENT:n.C_BLOCK_COMMENT_MODE,HEXCOLOR:{scope:"number",begin:/#(([0-9a-fA-F]{3,4})|(([0-9a-fA-F]{2}){3,4}))\b/},FUNCTION_DISPATCH:{className:"built_in",begin:/[\w-]+(?=\()/},ATTRIBUTE_SELECTOR_MODE:{scope:"selector-attr",begin:/\[/,end:/\]/,illegal:"$",contains:[n.APOS_STRING_MODE,n.QUOTE_STRING_MODE]},CSS_NUMBER_MODE:{scope:"number",begin:n.NUMBER_RE+"(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",relevance:0},CSS_VARIABLE:{className:"attr",begin:/--[A-Za-z_][A-Za-z0-9_-]*/}}),mv=["a","abbr","address","article","aside","audio","b","blockquote","body","button","canvas","caption","cite","code","dd","del","details","dfn","div","dl","dt","em","fieldset","figcaption","figure","footer","form","h1","h2","h3","h4","h5","h6","header","hgroup","html","i","iframe","img","input","ins","kbd","label","legend","li","main","mark","menu","nav","object","ol","optgroup","option","p","picture","q","quote","samp","section","select","source","span","strong","summary","sup","table","tbody","td","textarea","tfoot","th","thead","time","tr","ul","var","video"],gv=["defs","g","marker","mask","pattern","svg","switch","symbol","feBlend","feColorMatrix","feComponentTransfer","feComposite","feConvolveMatrix","feDiffuseLighting","feDisplacementMap","feFlood","feGaussianBlur","feImage","feMerge","feMorphology","feOffset","feSpecularLighting","feTile","feTurbulence","linearGradient","radialGradient","stop","circle","ellipse","image","line","path","polygon","polyline","rect","text","use","textPath","tspan","foreignObject","clipPath"],_v=[...mv,...gv],vv=["any-hover","any-pointer","aspect-ratio","color","color-gamut","color-index","device-aspect-ratio","device-height","device-width","display-mode","forced-colors","grid","height","hover","inverted-colors","monochrome","orientation","overflow-block","overflow-inline","pointer","prefers-color-scheme","prefers-contrast","prefers-reduced-motion","prefers-reduced-transparency","resolution","scan","scripting","update","width","min-width","max-width","min-height","max-height"].sort().reverse(),xv=["active","any-link","blank","checked","current","default","defined","dir","disabled","drop","empty","enabled","first","first-child","first-of-type","fullscreen","future","focus","focus-visible","focus-within","has","host","host-context","hover","indeterminate","in-range","invalid","is","lang","last-child","last-of-type","left","link","local-link","not","nth-child","nth-col","nth-last-child","nth-last-col","nth-last-of-type","nth-of-type","only-child","only-of-type","optional","out-of-range","past","placeholder-shown","read-only","read-write","required","right","root","scope","target","target-within","user-invalid","valid","visited","where"].sort().reverse(),bv=["after","backdrop","before","cue","cue-region","first-letter","first-line","grammar-error","marker","part","placeholder","selection","slotted","spelling-error"].sort().reverse(),Sv=["accent-color","align-content","align-items","align-self","alignment-baseline","all","anchor-name","animation","animation-composition","animation-delay","animation-direction","animation-duration","animation-fill-mode","animation-iteration-count","animation-name","animation-play-state","animation-range","animation-range-end","animation-range-start","animation-timeline","animation-timing-function","appearance","aspect-ratio","backdrop-filter","backface-visibility","background","background-attachment","background-blend-mode","background-clip","background-color","background-image","background-origin","background-position","background-position-x","background-position-y","background-repeat","background-size","baseline-shift","block-size","border","border-block","border-block-color","border-block-end","border-block-end-color","border-block-end-style","border-block-end-width","border-block-start","border-block-start-color","border-block-start-style","border-block-start-width","border-block-style","border-block-width","border-bottom","border-bottom-color","border-bottom-left-radius","border-bottom-right-radius","border-bottom-style","border-bottom-width","border-collapse","border-color","border-end-end-radius","border-end-start-radius","border-image","border-image-outset","border-image-repeat","border-image-slice","border-image-source","border-image-width","border-inline","border-inline-color","border-inline-end","border-inline-end-color","border-inline-end-style","border-inline-end-width","border-inline-start","border-inline-start-color","border-inline-start-style","border-inline-start-width","border-inline-style","border-inline-width","border-left","border-left-color","border-left-style","border-left-width","border-radius","border-right","border-right-color","border-right-style","border-right-width","border-spacing","border-start-end-radius","border-start-start-radius","border-style","border-top","border-top-color","border-top-left-radius","border-top-right-radius","border-top-style","border-top-width","border-width","bottom","box-align","box-decoration-break","box-direction","box-flex","box-flex-group","box-lines","box-ordinal-group","box-orient","box-pack","box-shadow","box-sizing","break-after","break-before","break-inside","caption-side","caret-color","clear","clip","clip-path","clip-rule","color","color-interpolation","color-interpolation-filters","color-profile","color-rendering","color-scheme","column-count","column-fill","column-gap","column-rule","column-rule-color","column-rule-style","column-rule-width","column-span","column-width","columns","contain","contain-intrinsic-block-size","contain-intrinsic-height","contain-intrinsic-inline-size","contain-intrinsic-size","contain-intrinsic-width","container","container-name","container-type","content","content-visibility","counter-increment","counter-reset","counter-set","cue","cue-after","cue-before","cursor","cx","cy","direction","display","dominant-baseline","empty-cells","enable-background","field-sizing","fill","fill-opacity","fill-rule","filter","flex","flex-basis","flex-direction","flex-flow","flex-grow","flex-shrink","flex-wrap","float","flood-color","flood-opacity","flow","font","font-display","font-family","font-feature-settings","font-kerning","font-language-override","font-optical-sizing","font-palette","font-size","font-size-adjust","font-smooth","font-smoothing","font-stretch","font-style","font-synthesis","font-synthesis-position","font-synthesis-small-caps","font-synthesis-style","font-synthesis-weight","font-variant","font-variant-alternates","font-variant-caps","font-variant-east-asian","font-variant-emoji","font-variant-ligatures","font-variant-numeric","font-variant-position","font-variation-settings","font-weight","forced-color-adjust","gap","glyph-orientation-horizontal","glyph-orientation-vertical","grid","grid-area","grid-auto-columns","grid-auto-flow","grid-auto-rows","grid-column","grid-column-end","grid-column-start","grid-gap","grid-row","grid-row-end","grid-row-start","grid-template","grid-template-areas","grid-template-columns","grid-template-rows","hanging-punctuation","height","hyphenate-character","hyphenate-limit-chars","hyphens","icon","image-orientation","image-rendering","image-resolution","ime-mode","initial-letter","initial-letter-align","inline-size","inset","inset-area","inset-block","inset-block-end","inset-block-start","inset-inline","inset-inline-end","inset-inline-start","isolation","justify-content","justify-items","justify-self","kerning","left","letter-spacing","lighting-color","line-break","line-height","line-height-step","list-style","list-style-image","list-style-position","list-style-type","margin","margin-block","margin-block-end","margin-block-start","margin-bottom","margin-inline","margin-inline-end","margin-inline-start","margin-left","margin-right","margin-top","margin-trim","marker","marker-end","marker-mid","marker-start","marks","mask","mask-border","mask-border-mode","mask-border-outset","mask-border-repeat","mask-border-slice","mask-border-source","mask-border-width","mask-clip","mask-composite","mask-image","mask-mode","mask-origin","mask-position","mask-repeat","mask-size","mask-type","masonry-auto-flow","math-depth","math-shift","math-style","max-block-size","max-height","max-inline-size","max-width","min-block-size","min-height","min-inline-size","min-width","mix-blend-mode","nav-down","nav-index","nav-left","nav-right","nav-up","none","normal","object-fit","object-position","offset","offset-anchor","offset-distance","offset-path","offset-position","offset-rotate","opacity","order","orphans","outline","outline-color","outline-offset","outline-style","outline-width","overflow","overflow-anchor","overflow-block","overflow-clip-margin","overflow-inline","overflow-wrap","overflow-x","overflow-y","overlay","overscroll-behavior","overscroll-behavior-block","overscroll-behavior-inline","overscroll-behavior-x","overscroll-behavior-y","padding","padding-block","padding-block-end","padding-block-start","padding-bottom","padding-inline","padding-inline-end","padding-inline-start","padding-left","padding-right","padding-top","page","page-break-after","page-break-before","page-break-inside","paint-order","pause","pause-after","pause-before","perspective","perspective-origin","place-content","place-items","place-self","pointer-events","position","position-anchor","position-visibility","print-color-adjust","quotes","r","resize","rest","rest-after","rest-before","right","rotate","row-gap","ruby-align","ruby-position","scale","scroll-behavior","scroll-margin","scroll-margin-block","scroll-margin-block-end","scroll-margin-block-start","scroll-margin-bottom","scroll-margin-inline","scroll-margin-inline-end","scroll-margin-inline-start","scroll-margin-left","scroll-margin-right","scroll-margin-top","scroll-padding","scroll-padding-block","scroll-padding-block-end","scroll-padding-block-start","scroll-padding-bottom","scroll-padding-inline","scroll-padding-inline-end","scroll-padding-inline-start","scroll-padding-left","scroll-padding-right","scroll-padding-top","scroll-snap-align","scroll-snap-stop","scroll-snap-type","scroll-timeline","scroll-timeline-axis","scroll-timeline-name","scrollbar-color","scrollbar-gutter","scrollbar-width","shape-image-threshold","shape-margin","shape-outside","shape-rendering","speak","speak-as","src","stop-color","stop-opacity","stroke","stroke-dasharray","stroke-dashoffset","stroke-linecap","stroke-linejoin","stroke-miterlimit","stroke-opacity","stroke-width","tab-size","table-layout","text-align","text-align-all","text-align-last","text-anchor","text-combine-upright","text-decoration","text-decoration-color","text-decoration-line","text-decoration-skip","text-decoration-skip-ink","text-decoration-style","text-decoration-thickness","text-emphasis","text-emphasis-color","text-emphasis-position","text-emphasis-style","text-indent","text-justify","text-orientation","text-overflow","text-rendering","text-shadow","text-size-adjust","text-transform","text-underline-offset","text-underline-position","text-wrap","text-wrap-mode","text-wrap-style","timeline-scope","top","touch-action","transform","transform-box","transform-origin","transform-style","transition","transition-behavior","transition-delay","transition-duration","transition-property","transition-timing-function","translate","unicode-bidi","user-modify","user-select","vector-effect","vertical-align","view-timeline","view-timeline-axis","view-timeline-inset","view-timeline-name","view-transition-name","visibility","voice-balance","voice-duration","voice-family","voice-pitch","voice-range","voice-rate","voice-stress","voice-volume","white-space","white-space-collapse","widows","width","will-change","word-break","word-spacing","word-wrap","writing-mode","x","y","z-index","zoom"].sort().reverse();function yv(n){const e=n.regex,t=pv(n),i={begin:/-(webkit|moz|ms|o)-(?=[a-z])/},r="and or not only",a=/@-?\w[\w]*(-\w+)*/,o="[a-zA-Z-][a-zA-Z0-9_-]*",l=[n.APOS_STRING_MODE,n.QUOTE_STRING_MODE];return{name:"CSS",case_insensitive:!0,illegal:/[=|'\$]/,keywords:{keyframePosition:"from to"},classNameAliases:{keyframePosition:"selector-tag"},contains:[t.BLOCK_COMMENT,i,t.CSS_NUMBER_MODE,{className:"selector-id",begin:/#[A-Za-z0-9_-]+/,relevance:0},{className:"selector-class",begin:"\\."+o,relevance:0},t.ATTRIBUTE_SELECTOR_MODE,{className:"selector-pseudo",variants:[{begin:":("+xv.join("|")+")"},{begin:":(:)?("+bv.join("|")+")"}]},t.CSS_VARIABLE,{className:"attribute",begin:"\\b("+Sv.join("|")+")\\b"},{begin:/:/,end:/[;}{]/,contains:[t.BLOCK_COMMENT,t.HEXCOLOR,t.IMPORTANT,t.CSS_NUMBER_MODE,...l,{begin:/(url|data-uri)\(/,end:/\)/,relevance:0,keywords:{built_in:"url data-uri"},contains:[...l,{className:"string",begin:/[^)]/,endsWithParent:!0,excludeEnd:!0}]},t.FUNCTION_DISPATCH]},{begin:e.lookahead(/@/),end:"[{;]",relevance:0,illegal:/:/,contains:[{className:"keyword",begin:a},{begin:/\s/,endsWithParent:!0,excludeEnd:!0,relevance:0,keywords:{$pattern:/[a-z-]+/,keyword:r,attribute:vv.join(" ")},contains:[{begin:/[a-z-]+(?=:)/,className:"attribute"},...l,t.CSS_NUMBER_MODE]}]},{className:"selector-tag",begin:"\\b("+_v.join("|")+")\\b"}]}}function Ev(n){const e=n.regex;return{name:"Diff",aliases:["patch"],contains:[{className:"meta",relevance:10,match:e.either(/^@@ +-\d+,\d+ +\+\d+,\d+ +@@/,/^\*\*\* +\d+,\d+ +\*\*\*\*$/,/^--- +\d+,\d+ +----$/)},{className:"comment",variants:[{begin:e.either(/Index: /,/^index/,/={3,}/,/^-{3}/,/^\*{3} /,/^\+{3}/,/^diff --git/),end:/$/},{match:/^\*{15}$/}]},{className:"addition",begin:/^\+/,end:/$/},{className:"deletion",begin:/^-/,end:/$/},{className:"addition",begin:/^!/,end:/$/}]}}function Mv(n){return{name:"Dockerfile",aliases:["docker"],case_insensitive:!0,keywords:["from","maintainer","expose","env","arg","user","onbuild","stopsignal"],contains:[n.HASH_COMMENT_MODE,n.APOS_STRING_MODE,n.QUOTE_STRING_MODE,n.NUMBER_MODE,{beginKeywords:"run cmd entrypoint volume add copy workdir label healthcheck shell",starts:{end:/[^\\]$/,subLanguage:"bash"}}],illegal:"</"}}function Tv(n){const a={keyword:["break","case","chan","const","continue","default","defer","else","fallthrough","for","func","go","goto","if","import","interface","map","package","range","return","select","struct","switch","type","var"],type:["bool","byte","complex64","complex128","error","float32","float64","int8","int16","int32","int64","string","uint8","uint16","uint32","uint64","int","uint","uintptr","rune"],literal:["true","false","iota","nil"],built_in:["append","cap","close","complex","copy","imag","len","make","new","panic","print","println","real","recover","delete"]};return{name:"Go",aliases:["golang"],keywords:a,illegal:"</",contains:[n.C_LINE_COMMENT_MODE,n.C_BLOCK_COMMENT_MODE,{className:"string",variants:[n.QUOTE_STRING_MODE,n.APOS_STRING_MODE,{begin:"`",end:"`"}]},{className:"number",variants:[{match:/-?\b0[xX]\.[a-fA-F0-9](_?[a-fA-F0-9])*[pP][+-]?\d(_?\d)*i?/,relevance:0},{match:/-?\b0[xX](_?[a-fA-F0-9])+((\.([a-fA-F0-9](_?[a-fA-F0-9])*)?)?[pP][+-]?\d(_?\d)*)?i?/,relevance:0},{match:/-?\b0[oO](_?[0-7])*i?/,relevance:0},{match:/-?\.\d(_?\d)*([eE][+-]?\d(_?\d)*)?i?/,relevance:0},{match:/-?\b\d(_?\d)*(\.(\d(_?\d)*)?)?([eE][+-]?\d(_?\d)*)?i?/,relevance:0}]},{begin:/:=/},{className:"function",beginKeywords:"func",end:"\\s*(\\{|$)",excludeEnd:!0,contains:[n.TITLE_MODE,{className:"params",begin:/\(/,end:/\)/,endsParent:!0,keywords:a,illegal:/["']/}]}]}}function wv(n){const e=n.regex,t={className:"number",relevance:0,variants:[{begin:/([+-]+)?[\d]+_[\d_]+/},{begin:n.NUMBER_RE}]},i=n.COMMENT();i.variants=[{begin:/;/,end:/$/},{begin:/#/,end:/$/}];const r={className:"variable",variants:[{begin:/\$[\w\d"][\w\d_]*/},{begin:/\$\{(.*?)\}/}]},a={className:"literal",begin:/\bon|off|true|false|yes|no\b/},o={className:"string",contains:[n.BACKSLASH_ESCAPE],variants:[{begin:"'''",end:"'''",relevance:10},{begin:'"""',end:'"""',relevance:10},{begin:'"',end:'"'},{begin:"'",end:"'"}]},l={begin:/\[/,end:/\]/,contains:[i,a,r,o,t,"self"],relevance:0},c=/[A-Za-z0-9_-]+/,u=/"(\\"|[^"])*"/,f=/'[^']*'/,h=e.either(c,u,f),d=e.concat(h,"(\\s*\\.\\s*",h,")*",e.lookahead(/\s*=\s*[^#\s]/));return{name:"TOML, also INI",aliases:["toml"],case_insensitive:!0,illegal:/\S/,contains:[i,{className:"section",begin:/\[+/,end:/\]+/},{begin:d,className:"attr",starts:{end:/$/,contains:[i,l,a,r,o,t]}}]}}const Sd="[A-Za-z$_][0-9A-Za-z$_]*",Av=["as","in","of","if","for","while","finally","var","new","function","do","return","void","else","break","catch","instanceof","with","throw","case","default","try","switch","continue","typeof","delete","let","yield","const","class","debugger","async","await","static","import","from","export","extends","using"],Rv=["true","false","null","undefined","NaN","Infinity"],Rh=["Object","Function","Boolean","Symbol","Math","Date","Number","BigInt","String","RegExp","Array","Float32Array","Float64Array","Int8Array","Uint8Array","Uint8ClampedArray","Int16Array","Int32Array","Uint16Array","Uint32Array","BigInt64Array","BigUint64Array","Set","Map","WeakSet","WeakMap","ArrayBuffer","SharedArrayBuffer","Atomics","DataView","JSON","Promise","Generator","GeneratorFunction","AsyncFunction","Reflect","Proxy","Intl","WebAssembly"],Ch=["Error","EvalError","InternalError","RangeError","ReferenceError","SyntaxError","TypeError","URIError"],Ih=["setInterval","setTimeout","clearInterval","clearTimeout","require","exports","eval","isFinite","isNaN","parseFloat","parseInt","decodeURI","decodeURIComponent","encodeURI","encodeURIComponent","escape","unescape"],Cv=["arguments","this","super","console","window","document","localStorage","sessionStorage","module","global"],Iv=[].concat(Ih,Rh,Ch);function Nh(n){const e=n.regex,t=(I,{after:F})=>{const Y="</"+I[0].slice(1);return I.input.indexOf(Y,F)!==-1},i=Sd,r={begin:"<>",end:"</>"},a=/<[A-Za-z0-9\\._:-]+\s*\/>/,o={begin:/<[A-Za-z0-9\\._:-]+/,end:/\/[A-Za-z0-9\\._:-]+>|\/>/,isTrulyOpeningTag:(I,F)=>{const Y=I[0].length+I.index,te=I.input[Y];if(te==="<"||te===","){F.ignoreMatch();return}te===">"&&(t(I,{after:Y})||F.ignoreMatch());let X;const K=I.input.substring(Y);if(X=K.match(/^\s*=/)){F.ignoreMatch();return}if((X=K.match(/^\s+extends\s+/))&&X.index===0){F.ignoreMatch();return}}},l={$pattern:Sd,keyword:Av,literal:Rv,built_in:Iv,"variable.language":Cv},c="[0-9](_?[0-9])*",u=`\\.(${c})`,f="0|[1-9](_?[0-9])*|0[0-7]*[89][0-9]*",h={className:"number",variants:[{begin:`(\\b(${f})((${u})|\\.)?|(${u}))[eE][+-]?(${c})\\b`},{begin:`\\b(${f})\\b((${u})\\b|\\.)?|(${u})\\b`},{begin:"\\b(0|[1-9](_?[0-9])*)n\\b"},{begin:"\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*n?\\b"},{begin:"\\b0[bB][0-1](_?[0-1])*n?\\b"},{begin:"\\b0[oO][0-7](_?[0-7])*n?\\b"},{begin:"\\b0[0-7]+n?\\b"}],relevance:0},d={className:"subst",begin:"\\$\\{",end:"\\}",keywords:l,contains:[]},p={begin:".?html`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"xml"}},m={begin:".?css`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"css"}},E={begin:".?gql`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"graphql"}},g={className:"string",begin:"`",end:"`",contains:[n.BACKSLASH_ESCAPE,d]},O={className:"comment",variants:[n.COMMENT(/\/\*\*(?!\/)/,"\\*/",{relevance:0,contains:[{begin:"(?=@[A-Za-z]+)",relevance:0,contains:[{className:"doctag",begin:"@[A-Za-z]+"},{className:"type",begin:"\\{",end:"\\}",excludeEnd:!0,excludeBegin:!0,relevance:0},{className:"variable",begin:i+"(?=\\s*(-)|$)",endsParent:!0,relevance:0},{begin:/(?=[^\n])\s/,relevance:0}]}]}),n.C_BLOCK_COMMENT_MODE,n.C_LINE_COMMENT_MODE]},D=[n.APOS_STRING_MODE,n.QUOTE_STRING_MODE,p,m,E,g,{match:/\$\d+/},h];d.contains=D.concat({begin:/\{/,end:/\}/,keywords:l,contains:["self"].concat(D)});const y=[].concat(O,d.contains),B=y.concat([{begin:/(\s*)\(/,end:/\)/,keywords:l,contains:["self"].concat(y)}]),R={className:"params",begin:/(\s*)\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:l,contains:B},C={variants:[{match:[/class/,/\s+/,i,/\s+/,/extends/,/\s+/,e.concat(i,"(",e.concat(/\./,i),")*")],scope:{1:"keyword",3:"title.class",5:"keyword",7:"title.class.inherited"}},{match:[/class/,/\s+/,i],scope:{1:"keyword",3:"title.class"}}]},b={relevance:0,match:e.either(/\bJSON/,/\b[A-Z][a-z]+([A-Z][a-z]*|\d)*/,/\b[A-Z]{2,}([A-Z][a-z]+|\d)+([A-Z][a-z]*)*/,/\b[A-Z]{2,}[a-z]+([A-Z][a-z]+|\d)*([A-Z][a-z]*)*/),className:"title.class",keywords:{_:[...Rh,...Ch]}},A={label:"use_strict",className:"meta",relevance:10,begin:/^\s*['"]use (strict|asm)['"]/},k={variants:[{match:[/function/,/\s+/,i,/(?=\s*\()/]},{match:[/function/,/\s*(?=\()/]}],className:{1:"keyword",3:"title.function"},label:"func.def",contains:[R],illegal:/%/},z={relevance:0,match:/\b[A-Z][A-Z_0-9]+\b/,className:"variable.constant"};function H(I){return e.concat("(?!",I.join("|"),")")}const q={match:e.concat(/\b/,H([...Ih,"super","import"].map(I=>`${I}\\s*\\(`)),i,e.lookahead(/\s*\(/)),className:"title.function",relevance:0},Q={begin:e.concat(/\./,e.lookahead(e.concat(i,/(?![0-9A-Za-z$_(])/))),end:i,excludeBegin:!0,keywords:"prototype",className:"property",relevance:0},G={match:[/get|set/,/\s+/,i,/(?=\()/],className:{1:"keyword",3:"title.function"},contains:[{begin:/\(\)/},R]},T="(\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)|"+n.UNDERSCORE_IDENT_RE+")\\s*=>",w={match:[/const|var|let/,/\s+/,i,/\s*/,/=\s*/,/(async\s*)?/,e.lookahead(T)],keywords:"async",className:{1:"keyword",3:"title.function"},contains:[R]};return{name:"JavaScript",aliases:["js","jsx","mjs","cjs"],keywords:l,exports:{PARAMS_CONTAINS:B,CLASS_REFERENCE:b},illegal:/#(?![$_A-z])/,contains:[n.SHEBANG({label:"shebang",binary:"node",relevance:5}),A,n.APOS_STRING_MODE,n.QUOTE_STRING_MODE,p,m,E,g,O,{match:/\$\d+/},h,b,{scope:"attr",match:i+e.lookahead(":"),relevance:0},w,{begin:"("+n.RE_STARTERS_RE+"|\\b(case|return|throw)\\b)\\s*",keywords:"return throw case",relevance:0,contains:[O,n.REGEXP_MODE,{className:"function",begin:T,returnBegin:!0,end:"\\s*=>",contains:[{className:"params",variants:[{begin:n.UNDERSCORE_IDENT_RE,relevance:0},{className:null,begin:/\(\s*\)/,skip:!0},{begin:/(\s*)\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:l,contains:B}]}]},{begin:/,/,relevance:0},{match:/\s+/,relevance:0},{variants:[{begin:r.begin,end:r.end},{match:a},{begin:o.begin,"on:begin":o.isTrulyOpeningTag,end:o.end}],subLanguage:"xml",contains:[{begin:o.begin,end:o.end,skip:!0,contains:["self"]}]}]},k,{beginKeywords:"while if switch catch for"},{begin:"\\b(?!function)"+n.UNDERSCORE_IDENT_RE+"\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)\\s*\\{",returnBegin:!0,label:"func.def",contains:[R,n.inherit(n.TITLE_MODE,{begin:i,className:"title.function"})]},{match:/\.\.\./,relevance:0},Q,{match:"\\$"+i,relevance:0},{match:[/\bconstructor(?=\s*\()/],className:{1:"title.function"},contains:[R]},q,z,C,G,{match:/\$[(.]/}]}}function Nv(n){const e={className:"attr",begin:/"(\\.|[^\\"\r\n])*"(?=\s*:)/,relevance:1.01},t={match:/[{}[\],:]/,className:"punctuation",relevance:0},i=["true","false","null"],r={scope:"literal",beginKeywords:i.join(" ")};return{name:"JSON",aliases:["jsonc"],keywords:{literal:i},contains:[e,t,n.QUOTE_STRING_MODE,r,n.C_NUMBER_MODE,n.C_LINE_COMMENT_MODE,n.C_BLOCK_COMMENT_MODE],illegal:"\\S"}}function Ph(n){const e=n.regex,t={begin:/<\/?[A-Za-z_]/,end:">",subLanguage:"xml",relevance:0},i={begin:"^[-\\*]{3,}",end:"$"},r={className:"code",variants:[{begin:"(`{3,})[^`](.|\\n)*?\\1`*[ ]*"},{begin:"(~{3,})[^~](.|\\n)*?\\1~*[ ]*"},{begin:"```",end:"```+[ ]*$"},{begin:"~~~",end:"~~~+[ ]*$"},{begin:"`.+?`"},{begin:"(?=^( {4}|\\t))",contains:[{begin:"^( {4}|\\t)",end:"(\\n)$"}],relevance:0}]},a={className:"bullet",begin:"^[ 	]*([*+-]|(\\d+\\.))(?=\\s+)",end:"\\s+",excludeEnd:!0},o={begin:/^\[[^\n]+\]:/,returnBegin:!0,contains:[{className:"symbol",begin:/\[/,end:/\]/,excludeBegin:!0,excludeEnd:!0},{className:"link",begin:/:\s*/,end:/$/,excludeBegin:!0}]},l=/[A-Za-z][A-Za-z0-9+.-]*/,c={variants:[{begin:/\[.+?\]\[.*?\]/,relevance:0},{begin:/\[.+?\]\(((data|javascript|mailto):|(?:http|ftp)s?:\/\/).*?\)/,relevance:2},{begin:e.concat(/\[.+?\]\(/,l,/:\/\/.*?\)/),relevance:2},{begin:/\[.+?\]\([./?&#].*?\)/,relevance:1},{begin:/\[.*?\]\(.*?\)/,relevance:0}],returnBegin:!0,contains:[{match:/\[(?=\])/},{className:"string",relevance:0,begin:"\\[",end:"\\]",excludeBegin:!0,returnEnd:!0},{className:"link",relevance:0,begin:"\\]\\(",end:"\\)",excludeBegin:!0,excludeEnd:!0},{className:"symbol",relevance:0,begin:"\\]\\[",end:"\\]",excludeBegin:!0,excludeEnd:!0}]},u={className:"strong",contains:[],variants:[{begin:/_{2}(?!\s)/,end:/_{2}/},{begin:/\*{2}(?!\s)/,end:/\*{2}/}]},f={className:"emphasis",contains:[],variants:[{begin:/\*(?![*\s])/,end:/\*/},{begin:/_(?![_\s])/,end:/_/,relevance:0}]},h=n.inherit(u,{contains:[]}),d=n.inherit(f,{contains:[]});u.contains.push(d),f.contains.push(h);let p=[t,c];return[u,f,h,d].forEach(_=>{_.contains=_.contains.concat(p)}),p=p.concat(u,f),{name:"Markdown",aliases:["md","mkdown","mkd"],contains:[{className:"section",variants:[{begin:"^#{1,6}",end:"$",contains:p},{begin:"(?=^.+?\\n[=-]{2,}$)",contains:[{begin:"^[=-]*$"},{begin:"^",end:"\\n",contains:p}]}]},t,a,u,f,{className:"quote",begin:"^>\\s+",contains:p,end:"$"},r,i,c,o,{scope:"literal",match:/&([a-zA-Z0-9]+|#[0-9]{1,7}|#[Xx][0-9a-fA-F]{1,6});/}]}}function Lh(n){const e=n.regex,t=new RegExp("[\\p{XID_Start}_]\\p{XID_Continue}*","u"),i=["and","as","assert","async","await","break","case","class","continue","def","del","elif","else","except","finally","for","from","global","if","import","in","is","lambda","match","nonlocal|10","not","or","pass","raise","return","try","while","with","yield"],l={$pattern:/[A-Za-z]\w+|__\w+__/,keyword:i,built_in:["__import__","abs","all","any","ascii","bin","bool","breakpoint","bytearray","bytes","callable","chr","classmethod","compile","complex","delattr","dict","dir","divmod","enumerate","eval","exec","filter","float","format","frozenset","getattr","globals","hasattr","hash","help","hex","id","input","int","isinstance","issubclass","iter","len","list","locals","map","max","memoryview","min","next","object","oct","open","ord","pow","print","property","range","repr","reversed","round","set","setattr","slice","sorted","staticmethod","str","sum","super","tuple","type","vars","zip"],literal:["__debug__","Ellipsis","False","None","NotImplemented","True"],type:["Any","Callable","Coroutine","Dict","List","Literal","Generic","Optional","Sequence","Set","Tuple","Type","Union"]},c={className:"meta",begin:/^(>>>|\.\.\.) /},u={className:"subst",begin:/\{/,end:/\}/,keywords:l,illegal:/#/},f={begin:/\{\{/,relevance:0},h={className:"string",contains:[n.BACKSLASH_ESCAPE],variants:[{begin:/([uU]|[bB]|[rR]|[bB][rR]|[rR][bB])?'''/,end:/'''/,contains:[n.BACKSLASH_ESCAPE,c],relevance:10},{begin:/([uU]|[bB]|[rR]|[bB][rR]|[rR][bB])?"""/,end:/"""/,contains:[n.BACKSLASH_ESCAPE,c],relevance:10},{begin:/([fF][rR]|[rR][fF]|[fF])'''/,end:/'''/,contains:[n.BACKSLASH_ESCAPE,c,f,u]},{begin:/([fF][rR]|[rR][fF]|[fF])"""/,end:/"""/,contains:[n.BACKSLASH_ESCAPE,c,f,u]},{begin:/([uU]|[rR])'/,end:/'/,relevance:10},{begin:/([uU]|[rR])"/,end:/"/,relevance:10},{begin:/([bB]|[bB][rR]|[rR][bB])'/,end:/'/},{begin:/([bB]|[bB][rR]|[rR][bB])"/,end:/"/},{begin:/([fF][rR]|[rR][fF]|[fF])'/,end:/'/,contains:[n.BACKSLASH_ESCAPE,f,u]},{begin:/([fF][rR]|[rR][fF]|[fF])"/,end:/"/,contains:[n.BACKSLASH_ESCAPE,f,u]},n.APOS_STRING_MODE,n.QUOTE_STRING_MODE]},d="[0-9](_?[0-9])*",p=`(\\b(${d}))?\\.(${d})|\\b(${d})\\.`,m=`\\b|${i.join("|")}`,E={className:"number",relevance:0,variants:[{begin:`(\\b(${d})|(${p}))[eE][+-]?(${d})[jJ]?(?=${m})`},{begin:`(${p})[jJ]?`},{begin:`\\b([1-9](_?[0-9])*|0+(_?0)*)[lLjJ]?(?=${m})`},{begin:`\\b0[bB](_?[01])+[lL]?(?=${m})`},{begin:`\\b0[oO](_?[0-7])+[lL]?(?=${m})`},{begin:`\\b0[xX](_?[0-9a-fA-F])+[lL]?(?=${m})`},{begin:`\\b(${d})[jJ](?=${m})`}]},g={className:"comment",begin:e.lookahead(/# type:/),end:/$/,keywords:l,contains:[{begin:/# type:/},{begin:/#/,end:/\b\B/,endsWithParent:!0}]},_={className:"params",variants:[{className:"",begin:/\(\s*\)/,skip:!0},{begin:/\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:l,contains:["self",c,E,h,n.HASH_COMMENT_MODE]}]};return u.contains=[h,E,c],{name:"Python",aliases:["py","gyp","ipython"],unicodeRegex:!0,keywords:l,illegal:/(<\/|\?)|=>/,contains:[c,E,{scope:"variable.language",match:/\bself\b/},{beginKeywords:"if",relevance:0},{match:/\bor\b/,scope:"keyword"},h,g,n.HASH_COMMENT_MODE,{match:[/\bdef/,/\s+/,t],scope:{1:"keyword",3:"title.function"},contains:[_]},{variants:[{match:[/\bclass/,/\s+/,t,/\s*/,/\(\s*/,t,/\s*\)/]},{match:[/\bclass/,/\s+/,t]}],scope:{1:"keyword",3:"title.class",6:"title.class.inherited"}},{className:"meta",begin:/^[\t ]*@/,end:/(?=#)|$/,contains:[E,_,h]}]}}function Dh(n){const e=n.regex,t=/(r#)?/,i=e.concat(t,n.UNDERSCORE_IDENT_RE),r=e.concat(t,n.IDENT_RE),a={className:"title.function.invoke",relevance:0,begin:e.concat(/\b/,/(?!let|for|while|if|else|match\b)/,r,e.lookahead(/\s*\(/))},o="([ui](8|16|32|64|128|size)|f(32|64))?",l=["abstract","as","async","await","become","box","break","const","continue","crate","do","dyn","else","enum","extern","false","final","fn","for","if","impl","in","let","loop","macro","match","mod","move","mut","override","priv","pub","ref","return","self","Self","static","struct","super","trait","true","try","type","typeof","union","unsafe","unsized","use","virtual","where","while","yield"],c=["true","false","Some","None","Ok","Err"],u=["drop ","Copy","Send","Sized","Sync","Drop","Fn","FnMut","FnOnce","ToOwned","Clone","Debug","PartialEq","PartialOrd","Eq","Ord","AsRef","AsMut","Into","From","Default","Iterator","Extend","IntoIterator","DoubleEndedIterator","ExactSizeIterator","SliceConcatExt","ToString","assert!","assert_eq!","bitflags!","bytes!","cfg!","col!","concat!","concat_idents!","debug_assert!","debug_assert_eq!","env!","eprintln!","panic!","file!","format!","format_args!","include_bytes!","include_str!","line!","local_data_key!","module_path!","option_env!","print!","println!","select!","stringify!","try!","unimplemented!","unreachable!","vec!","write!","writeln!","macro_rules!","assert_ne!","debug_assert_ne!"],f=["i8","i16","i32","i64","i128","isize","u8","u16","u32","u64","u128","usize","f32","f64","str","char","bool","Box","Option","Result","String","Vec"];return{name:"Rust",aliases:["rs"],keywords:{$pattern:n.IDENT_RE+"!?",type:f,keyword:l,literal:c,built_in:u},illegal:"</",contains:[n.C_LINE_COMMENT_MODE,n.COMMENT("/\\*","\\*/",{contains:["self"]}),n.inherit(n.QUOTE_STRING_MODE,{begin:/b?"/,illegal:null}),{className:"symbol",begin:/'[a-zA-Z_][a-zA-Z0-9_]*(?!')/},{scope:"string",variants:[{begin:/b?r(#*)"(.|\n)*?"\1(?!#)/},{begin:/b?'/,end:/'/,contains:[{scope:"char.escape",match:/\\('|\w|x\w{2}|u\w{4}|U\w{8})/}]}]},{className:"number",variants:[{begin:"\\b0b([01_]+)"+o},{begin:"\\b0o([0-7_]+)"+o},{begin:"\\b0x([A-Fa-f0-9_]+)"+o},{begin:"\\b(\\d[\\d_]*(\\.[0-9_]+)?([eE][+-]?[0-9_]+)?)"+o}],relevance:0},{begin:[/fn/,/\s+/,i],className:{1:"keyword",3:"title.function"}},{className:"meta",begin:"#!?\\[",end:"\\]",contains:[{className:"string",begin:/"/,end:/"/,contains:[n.BACKSLASH_ESCAPE]}]},{begin:[/let/,/\s+/,/(?:mut\s+)?/,i],className:{1:"keyword",3:"keyword",4:"variable"}},{begin:[/for/,/\s+/,i,/\s+/,/in/],className:{1:"keyword",3:"variable",5:"keyword"}},{begin:[/type/,/\s+/,i],className:{1:"keyword",3:"title.class"}},{begin:[/(?:trait|enum|struct|union|impl|for)/,/\s+/,i],className:{1:"keyword",3:"title.class"}},{begin:n.IDENT_RE+"::",keywords:{keyword:"Self",built_in:u,type:f}},{className:"punctuation",begin:"->"},a]}}function kh(n){return{name:"Shell Session",aliases:["console","shellsession"],contains:[{className:"meta.prompt",begin:/^\s{0,3}[/~\w\d[\]()@-]*[>%$#][ ]?/,starts:{end:/[^\\](?=\s*$)/,subLanguage:"bash"}}]}}function Pv(n){const e=n.regex,t=n.COMMENT("--","$"),i={scope:"string",variants:[{begin:/'/,end:/'/,contains:[{match:/''/}]}]},r={begin:/"/,end:/"/,contains:[{match:/""/}]},a=["true","false","unknown"],o=["double precision","large object","with timezone","without timezone"],l=["bigint","binary","blob","boolean","char","character","clob","date","dec","decfloat","decimal","float","int","integer","interval","nchar","nclob","national","numeric","real","row","smallint","time","timestamp","varchar","varying","varbinary"],c=["add","asc","collation","desc","final","first","last","view"],u=["abs","acos","all","allocate","alter","and","any","are","array","array_agg","array_max_cardinality","as","asensitive","asin","asymmetric","at","atan","atomic","authorization","avg","begin","begin_frame","begin_partition","between","bigint","binary","blob","boolean","both","by","call","called","cardinality","cascaded","case","cast","ceil","ceiling","char","char_length","character","character_length","check","classifier","clob","close","coalesce","collate","collect","column","commit","condition","connect","constraint","contains","convert","copy","corr","corresponding","cos","cosh","count","covar_pop","covar_samp","create","cross","cube","cume_dist","current","current_catalog","current_date","current_default_transform_group","current_path","current_role","current_row","current_schema","current_time","current_timestamp","current_path","current_role","current_transform_group_for_type","current_user","cursor","cycle","date","day","deallocate","dec","decimal","decfloat","declare","default","define","delete","dense_rank","deref","describe","deterministic","disconnect","distinct","double","drop","dynamic","each","element","else","empty","end","end_frame","end_partition","end-exec","equals","escape","every","except","exec","execute","exists","exp","external","extract","false","fetch","filter","first_value","float","floor","for","foreign","frame_row","free","from","full","function","fusion","get","global","grant","group","grouping","groups","having","hold","hour","identity","in","indicator","initial","inner","inout","insensitive","insert","int","integer","intersect","intersection","interval","into","is","join","json_array","json_arrayagg","json_exists","json_object","json_objectagg","json_query","json_table","json_table_primitive","json_value","lag","language","large","last_value","lateral","lead","leading","left","like","like_regex","listagg","ln","local","localtime","localtimestamp","log","log10","lower","match","match_number","match_recognize","matches","max","member","merge","method","min","minute","mod","modifies","module","month","multiset","national","natural","nchar","nclob","new","no","none","normalize","not","nth_value","ntile","null","nullif","numeric","octet_length","occurrences_regex","of","offset","old","omit","on","one","only","open","or","order","out","outer","over","overlaps","overlay","parameter","partition","pattern","per","percent","percent_rank","percentile_cont","percentile_disc","period","portion","position","position_regex","power","precedes","precision","prepare","primary","procedure","ptf","range","rank","reads","real","recursive","ref","references","referencing","regr_avgx","regr_avgy","regr_count","regr_intercept","regr_r2","regr_slope","regr_sxx","regr_sxy","regr_syy","release","result","return","returns","revoke","right","rollback","rollup","row","row_number","rows","running","savepoint","scope","scroll","search","second","seek","select","sensitive","session_user","set","show","similar","sin","sinh","skip","smallint","some","specific","specifictype","sql","sqlexception","sqlstate","sqlwarning","sqrt","start","static","stddev_pop","stddev_samp","submultiset","subset","substring","substring_regex","succeeds","sum","symmetric","system","system_time","system_user","table","tablesample","tan","tanh","then","time","timestamp","timezone_hour","timezone_minute","to","trailing","translate","translate_regex","translation","treat","trigger","trim","trim_array","true","truncate","uescape","union","unique","unknown","unnest","update","upper","user","using","value","values","value_of","var_pop","var_samp","varbinary","varchar","varying","versioning","when","whenever","where","width_bucket","window","with","within","without","year"],f=["abs","acos","array_agg","asin","atan","avg","cast","ceil","ceiling","coalesce","corr","cos","cosh","count","covar_pop","covar_samp","cume_dist","dense_rank","deref","element","exp","extract","first_value","floor","json_array","json_arrayagg","json_exists","json_object","json_objectagg","json_query","json_table","json_table_primitive","json_value","lag","last_value","lead","listagg","ln","log","log10","lower","max","min","mod","nth_value","ntile","nullif","percent_rank","percentile_cont","percentile_disc","position","position_regex","power","rank","regr_avgx","regr_avgy","regr_count","regr_intercept","regr_r2","regr_slope","regr_sxx","regr_sxy","regr_syy","row_number","sin","sinh","sqrt","stddev_pop","stddev_samp","substring","substring_regex","sum","tan","tanh","translate","translate_regex","treat","trim","trim_array","unnest","upper","value_of","var_pop","var_samp","width_bucket"],h=["current_catalog","current_date","current_default_transform_group","current_path","current_role","current_schema","current_transform_group_for_type","current_user","session_user","system_time","system_user","current_time","localtime","current_timestamp","localtimestamp"],d=["create table","insert into","primary key","foreign key","not null","alter table","add constraint","grouping sets","on overflow","character set","respect nulls","ignore nulls","nulls first","nulls last","depth first","breadth first"],p=f,m=[...u,...c].filter(B=>!f.includes(B)),E={scope:"variable",match:/@[a-z0-9][a-z0-9_]*/},g={scope:"operator",match:/[-+*/=%^~]|&&?|\|\|?|!=?|<(?:=>?|<|>)?|>[>=]?/,relevance:0},_={match:e.concat(/\b/,e.either(...p),/\s*\(/),relevance:0,keywords:{built_in:p}};function O(B){return e.concat(/\b/,e.either(...B.map(R=>R.replace(/\s+/,"\\s+"))),/\b/)}const D={scope:"keyword",match:O(d),relevance:0};function y(B,{exceptions:R,when:C}={}){const b=C;return R=R||[],B.map(A=>A.match(/\|\d+$/)||R.includes(A)?A:b(A)?`${A}|0`:A)}return{name:"SQL",case_insensitive:!0,illegal:/[{}]|<\//,keywords:{$pattern:/\b[\w\.]+/,keyword:y(m,{when:B=>B.length<3}),literal:a,type:l,built_in:h},contains:[{scope:"type",match:O(o)},D,_,E,i,r,n.C_NUMBER_MODE,n.C_BLOCK_COMMENT_MODE,t,g]}}const to="[A-Za-z$_][0-9A-Za-z$_]*",Uh=["as","in","of","if","for","while","finally","var","new","function","do","return","void","else","break","catch","instanceof","with","throw","case","default","try","switch","continue","typeof","delete","let","yield","const","class","debugger","async","await","static","import","from","export","extends","using"],Oh=["true","false","null","undefined","NaN","Infinity"],Fh=["Object","Function","Boolean","Symbol","Math","Date","Number","BigInt","String","RegExp","Array","Float32Array","Float64Array","Int8Array","Uint8Array","Uint8ClampedArray","Int16Array","Int32Array","Uint16Array","Uint32Array","BigInt64Array","BigUint64Array","Set","Map","WeakSet","WeakMap","ArrayBuffer","SharedArrayBuffer","Atomics","DataView","JSON","Promise","Generator","GeneratorFunction","AsyncFunction","Reflect","Proxy","Intl","WebAssembly"],Bh=["Error","EvalError","InternalError","RangeError","ReferenceError","SyntaxError","TypeError","URIError"],zh=["setInterval","setTimeout","clearInterval","clearTimeout","require","exports","eval","isFinite","isNaN","parseFloat","parseInt","decodeURI","decodeURIComponent","encodeURI","encodeURIComponent","escape","unescape"],Hh=["arguments","this","super","console","window","document","localStorage","sessionStorage","module","global"],Gh=[].concat(zh,Fh,Bh);function Lv(n){const e=n.regex,t=(I,{after:F})=>{const Y="</"+I[0].slice(1);return I.input.indexOf(Y,F)!==-1},i=to,r={begin:"<>",end:"</>"},a=/<[A-Za-z0-9\\._:-]+\s*\/>/,o={begin:/<[A-Za-z0-9\\._:-]+/,end:/\/[A-Za-z0-9\\._:-]+>|\/>/,isTrulyOpeningTag:(I,F)=>{const Y=I[0].length+I.index,te=I.input[Y];if(te==="<"||te===","){F.ignoreMatch();return}te===">"&&(t(I,{after:Y})||F.ignoreMatch());let X;const K=I.input.substring(Y);if(X=K.match(/^\s*=/)){F.ignoreMatch();return}if((X=K.match(/^\s+extends\s+/))&&X.index===0){F.ignoreMatch();return}}},l={$pattern:to,keyword:Uh,literal:Oh,built_in:Gh,"variable.language":Hh},c="[0-9](_?[0-9])*",u=`\\.(${c})`,f="0|[1-9](_?[0-9])*|0[0-7]*[89][0-9]*",h={className:"number",variants:[{begin:`(\\b(${f})((${u})|\\.)?|(${u}))[eE][+-]?(${c})\\b`},{begin:`\\b(${f})\\b((${u})\\b|\\.)?|(${u})\\b`},{begin:"\\b(0|[1-9](_?[0-9])*)n\\b"},{begin:"\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*n?\\b"},{begin:"\\b0[bB][0-1](_?[0-1])*n?\\b"},{begin:"\\b0[oO][0-7](_?[0-7])*n?\\b"},{begin:"\\b0[0-7]+n?\\b"}],relevance:0},d={className:"subst",begin:"\\$\\{",end:"\\}",keywords:l,contains:[]},p={begin:".?html`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"xml"}},m={begin:".?css`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"css"}},E={begin:".?gql`",end:"",starts:{end:"`",returnEnd:!1,contains:[n.BACKSLASH_ESCAPE,d],subLanguage:"graphql"}},g={className:"string",begin:"`",end:"`",contains:[n.BACKSLASH_ESCAPE,d]},O={className:"comment",variants:[n.COMMENT(/\/\*\*(?!\/)/,"\\*/",{relevance:0,contains:[{begin:"(?=@[A-Za-z]+)",relevance:0,contains:[{className:"doctag",begin:"@[A-Za-z]+"},{className:"type",begin:"\\{",end:"\\}",excludeEnd:!0,excludeBegin:!0,relevance:0},{className:"variable",begin:i+"(?=\\s*(-)|$)",endsParent:!0,relevance:0},{begin:/(?=[^\n])\s/,relevance:0}]}]}),n.C_BLOCK_COMMENT_MODE,n.C_LINE_COMMENT_MODE]},D=[n.APOS_STRING_MODE,n.QUOTE_STRING_MODE,p,m,E,g,{match:/\$\d+/},h];d.contains=D.concat({begin:/\{/,end:/\}/,keywords:l,contains:["self"].concat(D)});const y=[].concat(O,d.contains),B=y.concat([{begin:/(\s*)\(/,end:/\)/,keywords:l,contains:["self"].concat(y)}]),R={className:"params",begin:/(\s*)\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:l,contains:B},C={variants:[{match:[/class/,/\s+/,i,/\s+/,/extends/,/\s+/,e.concat(i,"(",e.concat(/\./,i),")*")],scope:{1:"keyword",3:"title.class",5:"keyword",7:"title.class.inherited"}},{match:[/class/,/\s+/,i],scope:{1:"keyword",3:"title.class"}}]},b={relevance:0,match:e.either(/\bJSON/,/\b[A-Z][a-z]+([A-Z][a-z]*|\d)*/,/\b[A-Z]{2,}([A-Z][a-z]+|\d)+([A-Z][a-z]*)*/,/\b[A-Z]{2,}[a-z]+([A-Z][a-z]+|\d)*([A-Z][a-z]*)*/),className:"title.class",keywords:{_:[...Fh,...Bh]}},A={label:"use_strict",className:"meta",relevance:10,begin:/^\s*['"]use (strict|asm)['"]/},k={variants:[{match:[/function/,/\s+/,i,/(?=\s*\()/]},{match:[/function/,/\s*(?=\()/]}],className:{1:"keyword",3:"title.function"},label:"func.def",contains:[R],illegal:/%/},z={relevance:0,match:/\b[A-Z][A-Z_0-9]+\b/,className:"variable.constant"};function H(I){return e.concat("(?!",I.join("|"),")")}const q={match:e.concat(/\b/,H([...zh,"super","import"].map(I=>`${I}\\s*\\(`)),i,e.lookahead(/\s*\(/)),className:"title.function",relevance:0},Q={begin:e.concat(/\./,e.lookahead(e.concat(i,/(?![0-9A-Za-z$_(])/))),end:i,excludeBegin:!0,keywords:"prototype",className:"property",relevance:0},G={match:[/get|set/,/\s+/,i,/(?=\()/],className:{1:"keyword",3:"title.function"},contains:[{begin:/\(\)/},R]},T="(\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)|"+n.UNDERSCORE_IDENT_RE+")\\s*=>",w={match:[/const|var|let/,/\s+/,i,/\s*/,/=\s*/,/(async\s*)?/,e.lookahead(T)],keywords:"async",className:{1:"keyword",3:"title.function"},contains:[R]};return{name:"JavaScript",aliases:["js","jsx","mjs","cjs"],keywords:l,exports:{PARAMS_CONTAINS:B,CLASS_REFERENCE:b},illegal:/#(?![$_A-z])/,contains:[n.SHEBANG({label:"shebang",binary:"node",relevance:5}),A,n.APOS_STRING_MODE,n.QUOTE_STRING_MODE,p,m,E,g,O,{match:/\$\d+/},h,b,{scope:"attr",match:i+e.lookahead(":"),relevance:0},w,{begin:"("+n.RE_STARTERS_RE+"|\\b(case|return|throw)\\b)\\s*",keywords:"return throw case",relevance:0,contains:[O,n.REGEXP_MODE,{className:"function",begin:T,returnBegin:!0,end:"\\s*=>",contains:[{className:"params",variants:[{begin:n.UNDERSCORE_IDENT_RE,relevance:0},{className:null,begin:/\(\s*\)/,skip:!0},{begin:/(\s*)\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:l,contains:B}]}]},{begin:/,/,relevance:0},{match:/\s+/,relevance:0},{variants:[{begin:r.begin,end:r.end},{match:a},{begin:o.begin,"on:begin":o.isTrulyOpeningTag,end:o.end}],subLanguage:"xml",contains:[{begin:o.begin,end:o.end,skip:!0,contains:["self"]}]}]},k,{beginKeywords:"while if switch catch for"},{begin:"\\b(?!function)"+n.UNDERSCORE_IDENT_RE+"\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)\\s*\\{",returnBegin:!0,label:"func.def",contains:[R,n.inherit(n.TITLE_MODE,{begin:i,className:"title.function"})]},{match:/\.\.\./,relevance:0},Q,{match:"\\$"+i,relevance:0},{match:[/\bconstructor(?=\s*\()/],className:{1:"title.function"},contains:[R]},q,z,C,G,{match:/\$[(.]/}]}}function Vh(n){const e=n.regex,t=Lv(n),i=to,r=["any","void","number","boolean","string","object","never","symbol","bigint","unknown"],a={begin:[/namespace/,/\s+/,n.IDENT_RE],beginScope:{1:"keyword",3:"title.class"}},o={beginKeywords:"interface",end:/\{/,excludeEnd:!0,keywords:{keyword:"interface extends",built_in:r},contains:[t.exports.CLASS_REFERENCE]},l={className:"meta",relevance:10,begin:/^\s*['"]use strict['"]/},c=["type","interface","public","private","protected","implements","declare","abstract","readonly","enum","override","satisfies"],u={$pattern:to,keyword:Uh.concat(c),literal:Oh,built_in:Gh.concat(r),"variable.language":Hh},f={className:"meta",begin:"@"+i},h=(E,g,_)=>{const O=E.contains.findIndex(D=>D.label===g);if(O===-1)throw new Error("can not find mode to replace");E.contains.splice(O,1,_)};Object.assign(t.keywords,u),t.exports.PARAMS_CONTAINS.push(f);const d=t.contains.find(E=>E.scope==="attr"),p=Object.assign({},d,{match:e.concat(i,e.lookahead(/\s*\?:/))});t.exports.PARAMS_CONTAINS.push([t.exports.CLASS_REFERENCE,d,p]),t.contains=t.contains.concat([f,a,o,p]),h(t,"shebang",n.SHEBANG()),h(t,"use_strict",l);const m=t.contains.find(E=>E.label==="func.def");return m.relevance=0,Object.assign(t,{name:"TypeScript",aliases:["ts","tsx","mts","cts"]}),t}function Wh(n){const e=n.regex,t=e.concat(/[\p{L}_]/u,e.optional(/[\p{L}0-9_.-]*:/u),/[\p{L}0-9_.-]*/u),i=/[\p{L}0-9._:-]+/u,r={className:"symbol",begin:/&[a-z]+;|&#[0-9]+;|&#x[a-f0-9]+;/},a={begin:/\s/,contains:[{className:"keyword",begin:/#?[a-z_][a-z1-9_-]+/,illegal:/\n/}]},o=n.inherit(a,{begin:/\(/,end:/\)/}),l=n.inherit(n.APOS_STRING_MODE,{className:"string"}),c=n.inherit(n.QUOTE_STRING_MODE,{className:"string"}),u={endsWithParent:!0,illegal:/</,relevance:0,contains:[{className:"attr",begin:i,relevance:0},{begin:/=\s*/,relevance:0,contains:[{className:"string",endsParent:!0,variants:[{begin:/"/,end:/"/,contains:[r]},{begin:/'/,end:/'/,contains:[r]},{begin:/[^\s"'=<>`]+/}]}]}]};return{name:"HTML, XML",aliases:["html","xhtml","rss","atom","xjb","xsd","xsl","plist","wsf","svg"],case_insensitive:!0,unicodeRegex:!0,contains:[{className:"meta",begin:/<![a-z]/,end:/>/,relevance:10,contains:[a,c,l,o,{begin:/\[/,end:/\]/,contains:[{className:"meta",begin:/<![a-z]/,end:/>/,contains:[a,o,c,l]}]}]},n.COMMENT(/<!--/,/-->/,{relevance:10}),{begin:/<!\[CDATA\[/,end:/\]\]>/,relevance:10},r,{className:"meta",end:/\?>/,variants:[{begin:/<\?xml/,relevance:10,contains:[c]},{begin:/<\?[a-z][a-z0-9]+/}]},{className:"tag",begin:/<style(?=\s|>)/,end:/>/,keywords:{name:"style"},contains:[u],starts:{end:/<\/style>/,returnEnd:!0,subLanguage:["css","xml"]}},{className:"tag",begin:/<script(?=\s|>)/,end:/>/,keywords:{name:"script"},contains:[u],starts:{end:/<\/script>/,returnEnd:!0,subLanguage:["javascript","handlebars","xml"]}},{className:"tag",begin:/<>|<\/>/},{className:"tag",begin:e.concat(/</,e.lookahead(e.concat(t,e.either(/\/>/,/>/,/\s/)))),end:/\/?>/,contains:[{className:"name",begin:t,relevance:0,starts:u}]},{className:"tag",begin:e.concat(/<\//,e.lookahead(e.concat(t,/>/))),contains:[{className:"name",begin:t,relevance:0},{begin:/>/,relevance:0,endsParent:!0}]}]}}function $h(n){const e="true false yes no null",t="[\\w#;/?:@&=+$,.~*'()[\\]]+",i={className:"attr",variants:[{begin:/[\w*@][\w*@ :()\./-]*:(?=[ \t]|$)/},{begin:/"[\w*@][\w*@ :()\./-]*":(?=[ \t]|$)/},{begin:/'[\w*@][\w*@ :()\./-]*':(?=[ \t]|$)/}]},r={className:"template-variable",variants:[{begin:/\{\{/,end:/\}\}/},{begin:/%\{/,end:/\}/}]},a={className:"string",relevance:0,begin:/'/,end:/'/,contains:[{match:/''/,scope:"char.escape",relevance:0}]},o={className:"string",relevance:0,variants:[{begin:/"/,end:/"/},{begin:/\S+/}],contains:[n.BACKSLASH_ESCAPE,r]},l=n.inherit(o,{variants:[{begin:/'/,end:/'/,contains:[{begin:/''/,relevance:0}]},{begin:/"/,end:/"/},{begin:/[^\s,{}[\]]+/}]}),d={className:"number",begin:"\\b"+"[0-9]{4}(-[0-9][0-9]){0,2}"+"([Tt \\t][0-9][0-9]?(:[0-9][0-9]){2})?"+"(\\.[0-9]*)?"+"([ \\t])*(Z|[-+][0-9][0-9]?(:[0-9][0-9])?)?"+"\\b"},p={end:",",endsWithParent:!0,excludeEnd:!0,keywords:e,relevance:0},m={begin:/\{/,end:/\}/,contains:[p],illegal:"\\n",relevance:0},E={begin:"\\[",end:"\\]",contains:[p],illegal:"\\n",relevance:0},g=[i,{className:"meta",begin:"^---\\s*$",relevance:10},{className:"string",begin:"[\\|>]([1-9]?[+-])?[ ]*\\n( +)[^ ][^\\n]*\\n(\\2[^\\n]+\\n?)*"},{begin:"<%[%=-]?",end:"[%-]?%>",subLanguage:"ruby",excludeBegin:!0,excludeEnd:!0,relevance:0},{className:"type",begin:"!\\w+!"+t},{className:"type",begin:"!<"+t+">"},{className:"type",begin:"!"+t},{className:"type",begin:"!!"+t},{className:"meta",begin:"&"+n.UNDERSCORE_IDENT_RE+"$"},{className:"meta",begin:"\\*"+n.UNDERSCORE_IDENT_RE+"$"},{className:"bullet",begin:"-(?=[ ]|$)",relevance:0},n.HASH_COMMENT_MODE,{beginKeywords:e,keywords:{literal:e}},d,{className:"number",begin:n.C_NUMBER_RE+"\\b",relevance:0},m,E,a,o],_=[...g];return _.pop(),_.push(l),p.contains=_,{name:"YAML",case_insensitive:!0,aliases:["yml"],contains:g}}function Oc(){return{async:!1,breaks:!1,extensions:null,gfm:!0,hooks:null,pedantic:!1,renderer:null,silent:!1,tokenizer:null,walkTokens:null}}var wr=Oc();function Xh(n){wr=n}var dr={exec:()=>null};function Ur(n){let e=[];return t=>{let i=Math.max(0,Math.min(3,t-1)),r=e[i];return r||(r=n(i),e[i]=r),r}}function Et(n,e=""){let t=typeof n=="string"?n:n.source,i={replace:(r,a)=>{let o=typeof a=="string"?a:a.source;return o=o.replace(dn.caret,"$1"),t=t.replace(r,o),i},getRegex:()=>new RegExp(t,e)};return i}var Dv=((n="")=>{try{return!!new RegExp("(?<=1)(?<!1)"+n)}catch{return!1}})(),dn={codeRemoveIndent:/^(?: {1,4}| {0,3}\t)/gm,outputLinkReplace:/\\([\[\]])/g,indentCodeCompensation:/^(\s+)(?:```)/,beginningSpace:/^\s+/,endingHash:/#$/,startingSpaceChar:/^ /,endingSpaceChar:/ $/,nonSpaceChar:/[^ ]/,newLineCharGlobal:/\n/g,tabCharGlobal:/\t/g,multipleSpaceGlobal:/\s+/g,blankLine:/^[ \t]*$/,doubleBlankLine:/\n[ \t]*\n[ \t]*$/,blockquoteStart:/^ {0,3}>/,blockquoteSetextReplace:/\n {0,3}((?:=+|-+) *)(?=\n|$)/g,blockquoteSetextReplace2:/^ {0,3}>[ \t]?/gm,listReplaceNesting:/^ {1,4}(?=( {4})*[^ ])/g,listIsTask:/^\[[ xX]\] +\S/,listReplaceTask:/^\[[ xX]\] +/,listTaskCheckbox:/\[[ xX]\]/,anyLine:/\n.*\n/,hrefBrackets:/^<(.*)>$/,tableDelimiter:/[:|]/,tableAlignChars:/^\||\| *$/g,tableRowBlankLine:/\n[ \t]*$/,tableAlignRight:/^ *-+: *$/,tableAlignCenter:/^ *:-+: *$/,tableAlignLeft:/^ *:-+ *$/,startATag:/^<a /i,endATag:/^<\/a>/i,startPreScriptTag:/^<(pre|code|kbd|script)(\s|>)/i,endPreScriptTag:/^<\/(pre|code|kbd|script)(\s|>)/i,startAngleBracket:/^</,endAngleBracket:/>$/,pedanticHrefTitle:/^([^'"]*[^\s])\s+(['"])(.*)\2/,unicodeAlphaNumeric:/[\p{L}\p{N}]/u,escapeTest:/[&<>"']/,escapeReplace:/[&<>"']/g,escapeTestNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/,escapeReplaceNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/g,caret:/(^|[^\[])\^/g,percentDecode:/%25/g,findPipe:/\|/g,splitPipe:/ \|/,slashPipe:/\\\|/g,carriageReturn:/\r\n|\r/g,spaceLine:/^ +$/gm,notSpaceStart:/^\S*/,endingNewline:/\n$/,listItemRegex:n=>new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`),nextBulletRegex:Ur(n=>new RegExp(`^ {0,${n}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`)),hrRegex:Ur(n=>new RegExp(`^ {0,${n}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`)),fencesBeginRegex:Ur(n=>new RegExp(`^ {0,${n}}(?:\`\`\`|~~~)`)),headingBeginRegex:Ur(n=>new RegExp(`^ {0,${n}}#`)),htmlBeginRegex:Ur(n=>new RegExp(`^ {0,${n}}<(?:[a-z].*>|!--)`,"i")),blockquoteBeginRegex:Ur(n=>new RegExp(`^ {0,${n}}>`))},kv=/^(?:[ \t]*(?:\n|$))+/,Uv=/^((?: {4}| {0,3}\t)[^\n]+(?:\n(?:[ \t]*(?:\n|$))*)?)+/,Ov=/^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/,is=/^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/,Fv=/^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/,Fc=/ {0,3}(?:[*+-]|\d{1,9}[.)])/,qh=/^(?!bull |blockCode|fences|blockquote|heading|html|table)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html|table))+?)\n {0,3}(=+|-+) *(?:\n+|$)/,Yh=Et(qh).replace(/bull/g,Fc).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/\|table/g,"").getRegex(),Bv=Et(qh).replace(/bull/g,Fc).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/table/g,/ {0,3}\|?(?:[:\- ]*\|)+[\:\- ]*\n/).getRegex(),Bc=/^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/,zv=/^[^\n]+/,zc=/(?!\s*\])(?:\\[\s\S]|[^\[\]\\])+/,Hv=Et(/^ {0,3}\[(label)\]: *(?:\n[ \t]*)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n[ \t]*)?| *\n[ \t]*)(title))? *(?:\n+|$)/).replace("label",zc).replace("title",/(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(),Gv=Et(/^(bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g,Fc).getRegex(),vo="address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul",Hc=/<!--(?:-?>|[\s\S]*?(?:-->|$))/,Vv=Et("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$))","i").replace("comment",Hc).replace("tag",vo).replace("attribute",/ +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(),Kh=Et(Bc).replace("hr",is).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("|table","").replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",vo).getRegex(),Wv=Et(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph",Kh).getRegex(),Gc={blockquote:Wv,code:Uv,def:Hv,fences:Ov,heading:Fv,hr:is,html:Vv,lheading:Yh,list:Gv,newline:kv,paragraph:Kh,table:dr,text:zv},yd=Et("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr",is).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("blockquote"," {0,3}>").replace("code","(?: {4}| {0,3}	)[^\\n]").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",vo).getRegex(),$v={...Gc,lheading:Bv,table:yd,paragraph:Et(Bc).replace("hr",is).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("table",yd).replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",vo).getRegex()},Xv={...Gc,html:Et(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment",Hc).replace(/tag/g,"(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),def:/^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,heading:/^(#{1,6})(.*)(?:\n+|$)/,fences:dr,lheading:/^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,paragraph:Et(Bc).replace("hr",is).replace("heading",` *#{1,6} *[^
]`).replace("lheading",Yh).replace("|table","").replace("blockquote"," {0,3}>").replace("|fences","").replace("|list","").replace("|html","").replace("|tag","").getRegex()},qv=/^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/,Yv=/^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/,Zh=/^( {2,}|\\)\n(?!\s*$)/,Kv=/^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/,fa=/[\p{P}\p{S}]/u,xo=/[\s\p{P}\p{S}]/u,Vc=/[^\s\p{P}\p{S}]/u,Zv=Et(/^((?![*_])punctSpace)/,"u").replace(/punctSpace/g,xo).getRegex(),Jh=/(?!~)[\p{P}\p{S}]/u,Jv=/(?!~)[\s\p{P}\p{S}]/u,Qv=/(?:[^\s\p{P}\p{S}]|~)/u,jv=Et(/link|precode-code|html/,"g").replace("link",/\[(?:[^\[\]`]|(?<a>`+)[^`]+\k<a>(?!`))*?\]\((?:\\[\s\S]|[^\\\(\)]|\((?:\\[\s\S]|[^\\\(\)])*\))*\)/).replace("precode-",Dv?"(?<!`)()":"(^^|[^`])").replace("code",/(?<b>`+)[^`]+\k<b>(?!`)/).replace("html",/<(?! )[^<>]*?>/).getRegex(),Qh=/^(?:\*+(?:((?!\*)punct)|([^\s*]))?)|^_+(?:((?!_)punct)|([^\s_]))?/,ex=Et(Qh,"u").replace(/punct/g,fa).getRegex(),tx=Et(Qh,"u").replace(/punct/g,Jh).getRegex(),jh="^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)punct(\\*+)(?=[\\s]|$)|notPunctSpace(\\*+)(?!\\*)(?=punctSpace|$)|(?!\\*)punctSpace(\\*+)(?=notPunctSpace)|[\\s](\\*+)(?!\\*)(?=punct)|(?!\\*)punct(\\*+)(?!\\*)(?=punct)|notPunctSpace(\\*+)(?=notPunctSpace)",nx=Et(jh,"gu").replace(/notPunctSpace/g,Vc).replace(/punctSpace/g,xo).replace(/punct/g,fa).getRegex(),ix=Et(jh,"gu").replace(/notPunctSpace/g,Qv).replace(/punctSpace/g,Jv).replace(/punct/g,Jh).getRegex(),rx=Et("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)punct(_+)(?=[\\s]|$)|notPunctSpace(_+)(?!_)(?=punctSpace|$)|(?!_)punctSpace(_+)(?=notPunctSpace)|[\\s](_+)(?!_)(?=punct)|(?!_)punct(_+)(?!_)(?=punct)","gu").replace(/notPunctSpace/g,Vc).replace(/punctSpace/g,xo).replace(/punct/g,fa).getRegex(),ax=Et(/^~~?(?:((?!~)punct)|[^\s~])/,"u").replace(/punct/g,fa).getRegex(),sx="^[^~]+(?=[^~])|(?!~)punct(~~?)(?=[\\s]|$)|notPunctSpace(~~?)(?!~)(?=punctSpace|$)|(?!~)punctSpace(~~?)(?=notPunctSpace)|[\\s](~~?)(?!~)(?=punct)|(?!~)punct(~~?)(?!~)(?=punct)|notPunctSpace(~~?)(?=notPunctSpace)",ox=Et(sx,"gu").replace(/notPunctSpace/g,Vc).replace(/punctSpace/g,xo).replace(/punct/g,fa).getRegex(),lx=Et(/\\(punct)/,"gu").replace(/punct/g,fa).getRegex(),cx=Et(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme",/[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email",/[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(),ux=Et(Hc).replace("(?:-->|$)","-->").getRegex(),dx=Et("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment",ux).replace("attribute",/\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(),no=/(?:\[(?:\\[\s\S]|[^\[\]\\])*\]|\\[\s\S]|`+(?!`)[^`]*?`+(?!`)|``+(?=\])|[^\[\]\\`])*?/,fx=Et(/^!?\[(label)\]\(\s*(href)(?:(?:[ \t]+(?:\n[ \t]*)?|\n[ \t]*)(title))?\s*\)/).replace("label",no).replace("href",/<(?:\\.|[^\n<>\\])+>|[^ \t\n\x00-\x1f]*/).replace("title",/"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(),ep=Et(/^!?\[(label)\]\[(ref)\]/).replace("label",no).replace("ref",zc).getRegex(),tp=Et(/^!?\[(ref)\](?:\[\])?/).replace("ref",zc).getRegex(),hx=Et("reflink|nolink(?!\\()","g").replace("reflink",ep).replace("nolink",tp).getRegex(),Ed=/[hH][tT][tT][pP][sS]?|[fF][tT][pP]/,Wc={_backpedal:dr,anyPunctuation:lx,autolink:cx,blockSkip:jv,br:Zh,code:Yv,del:dr,delLDelim:dr,delRDelim:dr,emStrongLDelim:ex,emStrongRDelimAst:nx,emStrongRDelimUnd:rx,escape:qv,link:fx,nolink:tp,punctuation:Zv,reflink:ep,reflinkSearch:hx,tag:dx,text:Kv,url:dr},px={...Wc,link:Et(/^!?\[(label)\]\((.*?)\)/).replace("label",no).getRegex(),reflink:Et(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label",no).getRegex()},Rl={...Wc,emStrongRDelimAst:ix,emStrongLDelim:tx,delLDelim:ax,delRDelim:ox,url:Et(/^((?:protocol):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/).replace("protocol",Ed).replace("email",/[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),_backpedal:/(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,del:/^(~~?)(?=[^\s~])((?:\\[\s\S]|[^\\])*?(?:\\[\s\S]|[^\s~\\]))\1(?=[^~]|$)/,text:Et(/^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|protocol:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/).replace("protocol",Ed).getRegex()},mx={...Rl,br:Et(Zh).replace("{2,}","*").getRegex(),text:Et(Rl.text).replace("\\b_","\\b_| {2,}\\n").replace(/\{2,\}/g,"*").getRegex()},_s={normal:Gc,gfm:$v,pedantic:Xv},Ea={normal:Wc,gfm:Rl,breaks:mx,pedantic:px},gx={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"},Md=n=>gx[n];function ii(n,e){if(e){if(dn.escapeTest.test(n))return n.replace(dn.escapeReplace,Md)}else if(dn.escapeTestNoEncode.test(n))return n.replace(dn.escapeReplaceNoEncode,Md);return n}function Td(n){try{n=encodeURI(n).replace(dn.percentDecode,"%")}catch{return null}return n}function wd(n,e){var a;let t=n.replace(dn.findPipe,(o,l,c)=>{let u=!1,f=l;for(;--f>=0&&c[f]==="\\";)u=!u;return u?"|":" |"}),i=t.split(dn.splitPipe),r=0;if(i[0].trim()||i.shift(),i.length>0&&!((a=i.at(-1))!=null&&a.trim())&&i.pop(),e)if(i.length>e)i.splice(e);else for(;i.length<e;)i.push("");for(;r<i.length;r++)i[r]=i[r].trim().replace(dn.slashPipe,"|");return i}function Wi(n,e,t){let i=n.length;if(i===0)return"";let r=0;for(;r<i&&n.charAt(i-r-1)===e;)r++;return n.slice(0,i-r)}function Ad(n){let e=n.split(`
`),t=e.length-1;for(;t>=0&&dn.blankLine.test(e[t]);)t--;return e.length-t<=2?n:e.slice(0,t+1).join(`
`)}function _x(n,e){if(n.indexOf(e[1])===-1)return-1;let t=0;for(let i=0;i<n.length;i++)if(n[i]==="\\")i++;else if(n[i]===e[0])t++;else if(n[i]===e[1]&&(t--,t<0))return i;return t>0?-2:-1}function vx(n,e=0){let t=e,i="";for(let r of n)if(r==="	"){let a=4-t%4;i+=" ".repeat(a),t+=a}else i+=r,t++;return i}function Rd(n,e,t,i,r){let a=e.href,o=e.title||null,l=n[1].replace(r.other.outputLinkReplace,"$1");i.state.inLink=!0;let c={type:n[0].charAt(0)==="!"?"image":"link",raw:t,href:a,title:o,text:l,tokens:i.inlineTokens(l)};return i.state.inLink=!1,c}function xx(n,e,t){let i=n.match(t.other.indentCodeCompensation);if(i===null)return e;let r=i[1];return e.split(`
`).map(a=>{let o=a.match(t.other.beginningSpace);if(o===null)return a;let[l]=o;return l.length>=r.length?a.slice(r.length):a}).join(`
`)}var io=class{constructor(n){Dt(this,"options");Dt(this,"rules");Dt(this,"lexer");this.options=n||wr}space(n){let e=this.rules.block.newline.exec(n);if(e&&e[0].length>0)return{type:"space",raw:e[0]}}code(n){let e=this.rules.block.code.exec(n);if(e){let t=this.options.pedantic?e[0]:Ad(e[0]),i=t.replace(this.rules.other.codeRemoveIndent,"");return{type:"code",raw:t,codeBlockStyle:"indented",text:i}}}fences(n){let e=this.rules.block.fences.exec(n);if(e){let t=e[0],i=xx(t,e[3]||"",this.rules);return{type:"code",raw:t,lang:e[2]?e[2].trim().replace(this.rules.inline.anyPunctuation,"$1"):e[2],text:i}}}heading(n){let e=this.rules.block.heading.exec(n);if(e){let t=e[2].trim();if(this.rules.other.endingHash.test(t)){let i=Wi(t,"#");(this.options.pedantic||!i||this.rules.other.endingSpaceChar.test(i))&&(t=i.trim())}return{type:"heading",raw:Wi(e[0],`
`),depth:e[1].length,text:t,tokens:this.lexer.inline(t)}}}hr(n){let e=this.rules.block.hr.exec(n);if(e)return{type:"hr",raw:Wi(e[0],`
`)}}blockquote(n){let e=this.rules.block.blockquote.exec(n);if(e){let t=Wi(e[0],`
`).split(`
`),i="",r="",a=[];for(;t.length>0;){let o=!1,l=[],c;for(c=0;c<t.length;c++)if(this.rules.other.blockquoteStart.test(t[c]))l.push(t[c]),o=!0;else if(!o)l.push(t[c]);else break;t=t.slice(c);let u=l.join(`
`),f=u.replace(this.rules.other.blockquoteSetextReplace,`
    $1`).replace(this.rules.other.blockquoteSetextReplace2,"");i=i?`${i}
${u}`:u,r=r?`${r}
${f}`:f;let h=this.lexer.state.top;if(this.lexer.state.top=!0,this.lexer.blockTokens(f,a,!0),this.lexer.state.top=h,t.length===0)break;let d=a.at(-1);if((d==null?void 0:d.type)==="code")break;if((d==null?void 0:d.type)==="blockquote"){let p=d,m=p.raw+`
`+t.join(`
`),E=this.blockquote(m);a[a.length-1]=E,i=i.substring(0,i.length-p.raw.length)+E.raw,r=r.substring(0,r.length-p.text.length)+E.text;break}else if((d==null?void 0:d.type)==="list"){let p=d,m=p.raw+`
`+t.join(`
`),E=this.list(m);a[a.length-1]=E,i=i.substring(0,i.length-d.raw.length)+E.raw,r=r.substring(0,r.length-p.raw.length)+E.raw,t=m.substring(a.at(-1).raw.length).split(`
`);continue}}return{type:"blockquote",raw:i,tokens:a,text:r}}}list(n){let e=this.rules.block.list.exec(n);if(e){let t=e[1].trim(),i=t.length>1,r={type:"list",raw:"",ordered:i,start:i?+t.slice(0,-1):"",loose:!1,items:[]};t=i?`\\d{1,9}\\${t.slice(-1)}`:`\\${t}`,this.options.pedantic&&(t=i?t:"[*+-]");let a=this.rules.other.listItemRegex(t),o=!1;for(;n;){let c=!1,u="",f="";if(!(e=a.exec(n))||this.rules.block.hr.test(n))break;u=e[0],n=n.substring(u.length);let h=vx(e[2].split(`
`,1)[0],e[1].length),d=n.split(`
`,1)[0],p=!h.trim(),m=0;if(this.options.pedantic?(m=2,f=h.trimStart()):p?m=e[1].length+1:(m=h.search(this.rules.other.nonSpaceChar),m=m>4?1:m,f=h.slice(m),m+=e[1].length),p&&this.rules.other.blankLine.test(d)&&(u+=d+`
`,n=n.substring(d.length+1),c=!0),!c){let E=this.rules.other.nextBulletRegex(m),g=this.rules.other.hrRegex(m),_=this.rules.other.fencesBeginRegex(m),O=this.rules.other.headingBeginRegex(m),D=this.rules.other.htmlBeginRegex(m),y=this.rules.other.blockquoteBeginRegex(m);for(;n;){let B=n.split(`
`,1)[0],R;if(d=B,this.options.pedantic?(d=d.replace(this.rules.other.listReplaceNesting,"  "),R=d):R=d.replace(this.rules.other.tabCharGlobal,"    "),_.test(d)||O.test(d)||D.test(d)||y.test(d)||E.test(d)||g.test(d))break;if(R.search(this.rules.other.nonSpaceChar)>=m||!d.trim())f+=`
`+R.slice(m);else{if(p||h.replace(this.rules.other.tabCharGlobal,"    ").search(this.rules.other.nonSpaceChar)>=4||_.test(h)||O.test(h)||g.test(h))break;f+=`
`+d}p=!d.trim(),u+=B+`
`,n=n.substring(B.length+1),h=R.slice(m)}}r.loose||(o?r.loose=!0:this.rules.other.doubleBlankLine.test(u)&&(o=!0)),r.items.push({type:"list_item",raw:u,task:!!this.options.gfm&&this.rules.other.listIsTask.test(f),loose:!1,text:f,tokens:[]}),r.raw+=u}let l=r.items.at(-1);if(l)l.raw=l.raw.trimEnd(),l.text=l.text.trimEnd();else return;r.raw=r.raw.trimEnd();for(let c of r.items){this.lexer.state.top=!1,c.tokens=this.lexer.blockTokens(c.text,[]);let u=c.tokens[0];if(c.task&&((u==null?void 0:u.type)==="text"||(u==null?void 0:u.type)==="paragraph")){c.text=c.text.replace(this.rules.other.listReplaceTask,""),u.raw=u.raw.replace(this.rules.other.listReplaceTask,""),u.text=u.text.replace(this.rules.other.listReplaceTask,"");for(let h=this.lexer.inlineQueue.length-1;h>=0;h--)if(this.rules.other.listIsTask.test(this.lexer.inlineQueue[h].src)){this.lexer.inlineQueue[h].src=this.lexer.inlineQueue[h].src.replace(this.rules.other.listReplaceTask,"");break}let f=this.rules.other.listTaskCheckbox.exec(c.raw);if(f){let h={type:"checkbox",raw:f[0]+" ",checked:f[0]!=="[ ]"};c.checked=h.checked,r.loose?c.tokens[0]&&["paragraph","text"].includes(c.tokens[0].type)&&"tokens"in c.tokens[0]&&c.tokens[0].tokens?(c.tokens[0].raw=h.raw+c.tokens[0].raw,c.tokens[0].text=h.raw+c.tokens[0].text,c.tokens[0].tokens.unshift(h)):c.tokens.unshift({type:"paragraph",raw:h.raw,text:h.raw,tokens:[h]}):c.tokens.unshift(h)}}else c.task&&(c.task=!1);if(!r.loose){let f=c.tokens.filter(d=>d.type==="space"),h=f.length>0&&f.some(d=>this.rules.other.anyLine.test(d.raw));r.loose=h}}if(r.loose)for(let c of r.items){c.loose=!0;for(let u of c.tokens)u.type==="text"&&(u.type="paragraph")}return r}}html(n){let e=this.rules.block.html.exec(n);if(e){let t=Ad(e[0]);return{type:"html",block:!0,raw:t,pre:e[1]==="pre"||e[1]==="script"||e[1]==="style",text:t}}}def(n){let e=this.rules.block.def.exec(n);if(e){let t=e[1].toLowerCase().replace(this.rules.other.multipleSpaceGlobal," "),i=e[2]?e[2].replace(this.rules.other.hrefBrackets,"$1").replace(this.rules.inline.anyPunctuation,"$1"):"",r=e[3]?e[3].substring(1,e[3].length-1).replace(this.rules.inline.anyPunctuation,"$1"):e[3];return{type:"def",tag:t,raw:Wi(e[0],`
`),href:i,title:r}}}table(n){var o;let e=this.rules.block.table.exec(n);if(!e||!this.rules.other.tableDelimiter.test(e[2]))return;let t=wd(e[1]),i=e[2].replace(this.rules.other.tableAlignChars,"").split("|"),r=(o=e[3])!=null&&o.trim()?e[3].replace(this.rules.other.tableRowBlankLine,"").split(`
`):[],a={type:"table",raw:Wi(e[0],`
`),header:[],align:[],rows:[]};if(t.length===i.length){for(let l of i)this.rules.other.tableAlignRight.test(l)?a.align.push("right"):this.rules.other.tableAlignCenter.test(l)?a.align.push("center"):this.rules.other.tableAlignLeft.test(l)?a.align.push("left"):a.align.push(null);for(let l=0;l<t.length;l++)a.header.push({text:t[l],tokens:this.lexer.inline(t[l]),header:!0,align:a.align[l]});for(let l of r)a.rows.push(wd(l,a.header.length).map((c,u)=>({text:c,tokens:this.lexer.inline(c),header:!1,align:a.align[u]})));return a}}lheading(n){let e=this.rules.block.lheading.exec(n);if(e){let t=e[1].trim();return{type:"heading",raw:Wi(e[0],`
`),depth:e[2].charAt(0)==="="?1:2,text:t,tokens:this.lexer.inline(t)}}}paragraph(n){let e=this.rules.block.paragraph.exec(n);if(e){let t=e[1].charAt(e[1].length-1)===`
`?e[1].slice(0,-1):e[1];return{type:"paragraph",raw:e[0],text:t,tokens:this.lexer.inline(t)}}}text(n){let e=this.rules.block.text.exec(n);if(e)return{type:"text",raw:e[0],text:e[0],tokens:this.lexer.inline(e[0])}}escape(n){let e=this.rules.inline.escape.exec(n);if(e)return{type:"escape",raw:e[0],text:e[1]}}tag(n){let e=this.rules.inline.tag.exec(n);if(e)return!this.lexer.state.inLink&&this.rules.other.startATag.test(e[0])?this.lexer.state.inLink=!0:this.lexer.state.inLink&&this.rules.other.endATag.test(e[0])&&(this.lexer.state.inLink=!1),!this.lexer.state.inRawBlock&&this.rules.other.startPreScriptTag.test(e[0])?this.lexer.state.inRawBlock=!0:this.lexer.state.inRawBlock&&this.rules.other.endPreScriptTag.test(e[0])&&(this.lexer.state.inRawBlock=!1),{type:"html",raw:e[0],inLink:this.lexer.state.inLink,inRawBlock:this.lexer.state.inRawBlock,block:!1,text:e[0]}}link(n){let e=this.rules.inline.link.exec(n);if(e){let t=e[2].trim();if(!this.options.pedantic&&this.rules.other.startAngleBracket.test(t)){if(!this.rules.other.endAngleBracket.test(t))return;let a=Wi(t.slice(0,-1),"\\");if((t.length-a.length)%2===0)return}else{let a=_x(e[2],"()");if(a===-2)return;if(a>-1){let o=(e[0].indexOf("!")===0?5:4)+e[1].length+a;e[2]=e[2].substring(0,a),e[0]=e[0].substring(0,o).trim(),e[3]=""}}let i=e[2],r="";if(this.options.pedantic){let a=this.rules.other.pedanticHrefTitle.exec(i);a&&(i=a[1],r=a[3])}else r=e[3]?e[3].slice(1,-1):"";return i=i.trim(),this.rules.other.startAngleBracket.test(i)&&(this.options.pedantic&&!this.rules.other.endAngleBracket.test(t)?i=i.slice(1):i=i.slice(1,-1)),Rd(e,{href:i&&i.replace(this.rules.inline.anyPunctuation,"$1"),title:r&&r.replace(this.rules.inline.anyPunctuation,"$1")},e[0],this.lexer,this.rules)}}reflink(n,e){let t;if((t=this.rules.inline.reflink.exec(n))||(t=this.rules.inline.nolink.exec(n))){let i=(t[2]||t[1]).replace(this.rules.other.multipleSpaceGlobal," "),r=e[i.toLowerCase()];if(!r){let a=t[0].charAt(0);return{type:"text",raw:a,text:a}}return Rd(t,r,t[0],this.lexer,this.rules)}}emStrong(n,e,t=""){let i=this.rules.inline.emStrongLDelim.exec(n);if(!(!i||!i[1]&&!i[2]&&!i[3]&&!i[4]||i[4]&&t.match(this.rules.other.unicodeAlphaNumeric))&&(!(i[1]||i[3])||!t||this.rules.inline.punctuation.exec(t))){let r=[...i[0]].length-1,a,o,l=r,c=0,u=i[0][0]==="*"?this.rules.inline.emStrongRDelimAst:this.rules.inline.emStrongRDelimUnd;for(u.lastIndex=0,e=e.slice(-1*n.length+r);(i=u.exec(e))!==null;){if(a=i[1]||i[2]||i[3]||i[4]||i[5]||i[6],!a)continue;if(o=[...a].length,i[3]||i[4]){l+=o;continue}else if((i[5]||i[6])&&r%3&&!((r+o)%3)){c+=o;continue}if(l-=o,l>0)continue;o=Math.min(o,o+l+c);let f=[...i[0]][0].length,h=n.slice(0,r+i.index+f+o);if(Math.min(r,o)%2){let p=h.slice(1,-1);return{type:"em",raw:h,text:p,tokens:this.lexer.inlineTokens(p)}}let d=h.slice(2,-2);return{type:"strong",raw:h,text:d,tokens:this.lexer.inlineTokens(d)}}}}codespan(n){let e=this.rules.inline.code.exec(n);if(e){let t=e[2].replace(this.rules.other.newLineCharGlobal," "),i=this.rules.other.nonSpaceChar.test(t),r=this.rules.other.startingSpaceChar.test(t)&&this.rules.other.endingSpaceChar.test(t);return i&&r&&(t=t.substring(1,t.length-1)),{type:"codespan",raw:e[0],text:t}}}br(n){let e=this.rules.inline.br.exec(n);if(e)return{type:"br",raw:e[0]}}del(n,e,t=""){let i=this.rules.inline.delLDelim.exec(n);if(i&&(!i[1]||!t||this.rules.inline.punctuation.exec(t))){let r=[...i[0]].length-1,a,o,l=r,c=this.rules.inline.delRDelim;for(c.lastIndex=0,e=e.slice(-1*n.length+r);(i=c.exec(e))!==null;){if(a=i[1]||i[2]||i[3]||i[4]||i[5]||i[6],!a||(o=[...a].length,o!==r))continue;if(i[3]||i[4]){l+=o;continue}if(l-=o,l>0)continue;o=Math.min(o,o+l);let u=[...i[0]][0].length,f=n.slice(0,r+i.index+u+o),h=f.slice(r,-r);return{type:"del",raw:f,text:h,tokens:this.lexer.inlineTokens(h)}}}}autolink(n){let e=this.rules.inline.autolink.exec(n);if(e){let t,i;return e[2]==="@"?(t=e[1],i="mailto:"+t):(t=e[1],i=t),{type:"link",raw:e[0],text:t,href:i,tokens:[{type:"text",raw:t,text:t}]}}}url(n){var t;let e;if(e=this.rules.inline.url.exec(n)){let i,r;if(e[2]==="@")i=e[0],r="mailto:"+i;else{let a;do a=e[0],e[0]=((t=this.rules.inline._backpedal.exec(e[0]))==null?void 0:t[0])??"";while(a!==e[0]);i=e[0],e[1]==="www."?r="http://"+e[0]:r=e[0]}return{type:"link",raw:e[0],text:i,href:r,tokens:[{type:"text",raw:i,text:i}]}}}inlineText(n){let e=this.rules.inline.text.exec(n);if(e){let t=this.lexer.state.inRawBlock;return{type:"text",raw:e[0],text:e[0],escaped:t}}}},Gn=class Cl{constructor(e){Dt(this,"tokens");Dt(this,"options");Dt(this,"state");Dt(this,"inlineQueue");Dt(this,"tokenizer");this.tokens=[],this.tokens.links=Object.create(null),this.options=e||wr,this.options.tokenizer=this.options.tokenizer||new io,this.tokenizer=this.options.tokenizer,this.tokenizer.options=this.options,this.tokenizer.lexer=this,this.inlineQueue=[],this.state={inLink:!1,inRawBlock:!1,top:!0};let t={other:dn,block:_s.normal,inline:Ea.normal};this.options.pedantic?(t.block=_s.pedantic,t.inline=Ea.pedantic):this.options.gfm&&(t.block=_s.gfm,this.options.breaks?t.inline=Ea.breaks:t.inline=Ea.gfm),this.tokenizer.rules=t}static get rules(){return{block:_s,inline:Ea}}static lex(e,t){return new Cl(t).lex(e)}static lexInline(e,t){return new Cl(t).inlineTokens(e)}lex(e){e=e.replace(dn.carriageReturn,`
`),this.blockTokens(e,this.tokens);for(let t=0;t<this.inlineQueue.length;t++){let i=this.inlineQueue[t];this.inlineTokens(i.src,i.tokens)}return this.inlineQueue=[],this.tokens}blockTokens(e,t=[],i=!1){var a,o,l;this.tokenizer.lexer=this,this.options.pedantic&&(e=e.replace(dn.tabCharGlobal,"    ").replace(dn.spaceLine,""));let r=1/0;for(;e;){if(e.length<r)r=e.length;else{this.infiniteLoopError(e.charCodeAt(0));break}let c;if((o=(a=this.options.extensions)==null?void 0:a.block)!=null&&o.some(f=>(c=f.call({lexer:this},e,t))?(e=e.substring(c.raw.length),t.push(c),!0):!1))continue;if(c=this.tokenizer.space(e)){e=e.substring(c.raw.length);let f=t.at(-1);c.raw.length===1&&f!==void 0?f.raw+=`
`:t.push(c);continue}if(c=this.tokenizer.code(e)){e=e.substring(c.raw.length);let f=t.at(-1);(f==null?void 0:f.type)==="paragraph"||(f==null?void 0:f.type)==="text"?(f.raw+=(f.raw.endsWith(`
`)?"":`
`)+c.raw,f.text+=`
`+c.text,this.inlineQueue.at(-1).src=f.text):t.push(c);continue}if(c=this.tokenizer.fences(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.heading(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.hr(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.blockquote(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.list(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.html(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.def(e)){e=e.substring(c.raw.length);let f=t.at(-1);(f==null?void 0:f.type)==="paragraph"||(f==null?void 0:f.type)==="text"?(f.raw+=(f.raw.endsWith(`
`)?"":`
`)+c.raw,f.text+=`
`+c.raw,this.inlineQueue.at(-1).src=f.text):this.tokens.links[c.tag]||(this.tokens.links[c.tag]={href:c.href,title:c.title},t.push(c));continue}if(c=this.tokenizer.table(e)){e=e.substring(c.raw.length),t.push(c);continue}if(c=this.tokenizer.lheading(e)){e=e.substring(c.raw.length),t.push(c);continue}let u=e;if((l=this.options.extensions)!=null&&l.startBlock){let f=1/0,h=e.slice(1),d;this.options.extensions.startBlock.forEach(p=>{d=p.call({lexer:this},h),typeof d=="number"&&d>=0&&(f=Math.min(f,d))}),f<1/0&&f>=0&&(u=e.substring(0,f+1))}if(this.state.top&&(c=this.tokenizer.paragraph(u))){let f=t.at(-1);i&&(f==null?void 0:f.type)==="paragraph"?(f.raw+=(f.raw.endsWith(`
`)?"":`
`)+c.raw,f.text+=`
`+c.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=f.text):t.push(c),i=u.length!==e.length,e=e.substring(c.raw.length);continue}if(c=this.tokenizer.text(e)){e=e.substring(c.raw.length);let f=t.at(-1);(f==null?void 0:f.type)==="text"?(f.raw+=(f.raw.endsWith(`
`)?"":`
`)+c.raw,f.text+=`
`+c.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=f.text):t.push(c);continue}if(e){this.infiniteLoopError(e.charCodeAt(0));break}}return this.state.top=!0,t}inline(e,t=[]){return this.inlineQueue.push({src:e,tokens:t}),t}inlineTokens(e,t=[]){var u,f,h,d,p;this.tokenizer.lexer=this;let i=e,r=null;if(this.tokens.links){let m=Object.keys(this.tokens.links);if(m.length>0)for(;(r=this.tokenizer.rules.inline.reflinkSearch.exec(i))!==null;)m.includes(r[0].slice(r[0].lastIndexOf("[")+1,-1))&&(i=i.slice(0,r.index)+"["+"a".repeat(r[0].length-2)+"]"+i.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex))}for(;(r=this.tokenizer.rules.inline.anyPunctuation.exec(i))!==null;)i=i.slice(0,r.index)+"++"+i.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);let a;for(;(r=this.tokenizer.rules.inline.blockSkip.exec(i))!==null;)a=r[2]?r[2].length:0,i=i.slice(0,r.index+a)+"["+"a".repeat(r[0].length-a-2)+"]"+i.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);i=((f=(u=this.options.hooks)==null?void 0:u.emStrongMask)==null?void 0:f.call({lexer:this},i))??i;let o=!1,l="",c=1/0;for(;e;){if(e.length<c)c=e.length;else{this.infiniteLoopError(e.charCodeAt(0));break}o||(l=""),o=!1;let m;if((d=(h=this.options.extensions)==null?void 0:h.inline)!=null&&d.some(g=>(m=g.call({lexer:this},e,t))?(e=e.substring(m.raw.length),t.push(m),!0):!1))continue;if(m=this.tokenizer.escape(e)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.tag(e)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.link(e)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.reflink(e,this.tokens.links)){e=e.substring(m.raw.length);let g=t.at(-1);m.type==="text"&&(g==null?void 0:g.type)==="text"?(g.raw+=m.raw,g.text+=m.text):t.push(m);continue}if(m=this.tokenizer.emStrong(e,i,l)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.codespan(e)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.br(e)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.del(e,i,l)){e=e.substring(m.raw.length),t.push(m);continue}if(m=this.tokenizer.autolink(e)){e=e.substring(m.raw.length),t.push(m);continue}if(!this.state.inLink&&(m=this.tokenizer.url(e))){e=e.substring(m.raw.length),t.push(m);continue}let E=e;if((p=this.options.extensions)!=null&&p.startInline){let g=1/0,_=e.slice(1),O;this.options.extensions.startInline.forEach(D=>{O=D.call({lexer:this},_),typeof O=="number"&&O>=0&&(g=Math.min(g,O))}),g<1/0&&g>=0&&(E=e.substring(0,g+1))}if(m=this.tokenizer.inlineText(E)){e=e.substring(m.raw.length),m.raw.slice(-1)!=="_"&&(l=m.raw.slice(-1)),o=!0;let g=t.at(-1);(g==null?void 0:g.type)==="text"?(g.raw+=m.raw,g.text+=m.text):t.push(m);continue}if(e){this.infiniteLoopError(e.charCodeAt(0));break}}return t}infiniteLoopError(e){let t="Infinite loop on byte: "+e;if(this.options.silent)console.error(t);else throw new Error(t)}},ro=class{constructor(n){Dt(this,"options");Dt(this,"parser");this.options=n||wr}space(n){return""}code({text:n,lang:e,escaped:t}){var a;let i=(a=(e||"").match(dn.notSpaceStart))==null?void 0:a[0],r=n.replace(dn.endingNewline,"")+`
`;return i?'<pre><code class="language-'+ii(i)+'">'+(t?r:ii(r,!0))+`</code></pre>
`:"<pre><code>"+(t?r:ii(r,!0))+`</code></pre>
`}blockquote({tokens:n}){return`<blockquote>
${this.parser.parse(n)}</blockquote>
`}html({text:n}){return n}def(n){return""}heading({tokens:n,depth:e}){return`<h${e}>${this.parser.parseInline(n)}</h${e}>
`}hr(n){return`<hr>
`}list(n){let e=n.ordered,t=n.start,i="";for(let o=0;o<n.items.length;o++){let l=n.items[o];i+=this.listitem(l)}let r=e?"ol":"ul",a=e&&t!==1?' start="'+t+'"':"";return"<"+r+a+`>
`+i+"</"+r+`>
`}listitem(n){return`<li>${this.parser.parse(n.tokens)}</li>
`}checkbox({checked:n}){return"<input "+(n?'checked="" ':"")+'disabled="" type="checkbox"> '}paragraph({tokens:n}){return`<p>${this.parser.parseInline(n)}</p>
`}table(n){let e="",t="";for(let r=0;r<n.header.length;r++)t+=this.tablecell(n.header[r]);e+=this.tablerow({text:t});let i="";for(let r=0;r<n.rows.length;r++){let a=n.rows[r];t="";for(let o=0;o<a.length;o++)t+=this.tablecell(a[o]);i+=this.tablerow({text:t})}return i&&(i=`<tbody>${i}</tbody>`),`<table>
<thead>
`+e+`</thead>
`+i+`</table>
`}tablerow({text:n}){return`<tr>
${n}</tr>
`}tablecell(n){let e=this.parser.parseInline(n.tokens),t=n.header?"th":"td";return(n.align?`<${t} align="${n.align}">`:`<${t}>`)+e+`</${t}>
`}strong({tokens:n}){return`<strong>${this.parser.parseInline(n)}</strong>`}em({tokens:n}){return`<em>${this.parser.parseInline(n)}</em>`}codespan({text:n}){return`<code>${ii(n,!0)}</code>`}br(n){return"<br>"}del({tokens:n}){return`<del>${this.parser.parseInline(n)}</del>`}link({href:n,title:e,tokens:t}){let i=this.parser.parseInline(t),r=Td(n);if(r===null)return i;n=r;let a='<a href="'+n+'"';return e&&(a+=' title="'+ii(e)+'"'),a+=">"+i+"</a>",a}image({href:n,title:e,text:t,tokens:i}){i&&(t=this.parser.parseInline(i,this.parser.textRenderer));let r=Td(n);if(r===null)return ii(t);n=r;let a=`<img src="${n}" alt="${ii(t)}"`;return e&&(a+=` title="${ii(e)}"`),a+=">",a}text(n){return"tokens"in n&&n.tokens?this.parser.parseInline(n.tokens):"escaped"in n&&n.escaped?n.text:ii(n.text)}},$c=class{strong({text:n}){return n}em({text:n}){return n}codespan({text:n}){return n}del({text:n}){return n}html({text:n}){return n}text({text:n}){return n}link({text:n}){return""+n}image({text:n}){return""+n}br(){return""}checkbox({raw:n}){return n}},Vn=class Il{constructor(e){Dt(this,"options");Dt(this,"renderer");Dt(this,"textRenderer");this.options=e||wr,this.options.renderer=this.options.renderer||new ro,this.renderer=this.options.renderer,this.renderer.options=this.options,this.renderer.parser=this,this.textRenderer=new $c}static parse(e,t){return new Il(t).parse(e)}static parseInline(e,t){return new Il(t).parseInline(e)}parse(e){var i,r;this.renderer.parser=this;let t="";for(let a=0;a<e.length;a++){let o=e[a];if((r=(i=this.options.extensions)==null?void 0:i.renderers)!=null&&r[o.type]){let c=o,u=this.options.extensions.renderers[c.type].call({parser:this},c);if(u!==!1||!["space","hr","heading","code","table","blockquote","list","html","def","paragraph","text"].includes(c.type)){t+=u||"";continue}}let l=o;switch(l.type){case"space":{t+=this.renderer.space(l);break}case"hr":{t+=this.renderer.hr(l);break}case"heading":{t+=this.renderer.heading(l);break}case"code":{t+=this.renderer.code(l);break}case"table":{t+=this.renderer.table(l);break}case"blockquote":{t+=this.renderer.blockquote(l);break}case"list":{t+=this.renderer.list(l);break}case"checkbox":{t+=this.renderer.checkbox(l);break}case"html":{t+=this.renderer.html(l);break}case"def":{t+=this.renderer.def(l);break}case"paragraph":{t+=this.renderer.paragraph(l);break}case"text":{t+=this.renderer.text(l);break}default:{let c='Token with "'+l.type+'" type was not found.';if(this.options.silent)return console.error(c),"";throw new Error(c)}}}return t}parseInline(e,t=this.renderer){var r,a;this.renderer.parser=this;let i="";for(let o=0;o<e.length;o++){let l=e[o];if((a=(r=this.options.extensions)==null?void 0:r.renderers)!=null&&a[l.type]){let u=this.options.extensions.renderers[l.type].call({parser:this},l);if(u!==!1||!["escape","html","link","image","strong","em","codespan","br","del","text"].includes(l.type)){i+=u||"";continue}}let c=l;switch(c.type){case"escape":{i+=t.text(c);break}case"html":{i+=t.html(c);break}case"link":{i+=t.link(c);break}case"image":{i+=t.image(c);break}case"checkbox":{i+=t.checkbox(c);break}case"strong":{i+=t.strong(c);break}case"em":{i+=t.em(c);break}case"codespan":{i+=t.codespan(c);break}case"br":{i+=t.br(c);break}case"del":{i+=t.del(c);break}case"text":{i+=t.text(c);break}default:{let u='Token with "'+c.type+'" type was not found.';if(this.options.silent)return console.error(u),"";throw new Error(u)}}}return i}},Gs,Ua=(Gs=class{constructor(n){Dt(this,"options");Dt(this,"block");this.options=n||wr}preprocess(n){return n}postprocess(n){return n}processAllTokens(n){return n}emStrongMask(n){return n}provideLexer(n=this.block){return n?Gn.lex:Gn.lexInline}provideParser(n=this.block){return n?Vn.parse:Vn.parseInline}},Dt(Gs,"passThroughHooks",new Set(["preprocess","postprocess","processAllTokens","emStrongMask"])),Dt(Gs,"passThroughHooksRespectAsync",new Set(["preprocess","postprocess","processAllTokens"])),Gs),np=class{constructor(...n){Dt(this,"defaults",Oc());Dt(this,"options",this.setOptions);Dt(this,"parse",this.parseMarkdown(!0));Dt(this,"parseInline",this.parseMarkdown(!1));Dt(this,"Parser",Vn);Dt(this,"Renderer",ro);Dt(this,"TextRenderer",$c);Dt(this,"Lexer",Gn);Dt(this,"Tokenizer",io);Dt(this,"Hooks",Ua);this.use(...n)}walkTokens(n,e){var i,r;let t=[];for(let a of n)switch(t=t.concat(e.call(this,a)),a.type){case"table":{let o=a;for(let l of o.header)t=t.concat(this.walkTokens(l.tokens,e));for(let l of o.rows)for(let c of l)t=t.concat(this.walkTokens(c.tokens,e));break}case"list":{let o=a;t=t.concat(this.walkTokens(o.items,e));break}default:{let o=a;(r=(i=this.defaults.extensions)==null?void 0:i.childTokens)!=null&&r[o.type]?this.defaults.extensions.childTokens[o.type].forEach(l=>{let c=o[l].flat(1/0);t=t.concat(this.walkTokens(c,e))}):o.tokens&&(t=t.concat(this.walkTokens(o.tokens,e)))}}return t}use(...n){let e=this.defaults.extensions||{renderers:{},childTokens:{}};return n.forEach(t=>{let i={...t};if(i.async=this.defaults.async||i.async||!1,t.extensions&&(t.extensions.forEach(r=>{if(!r.name)throw new Error("extension name required");if("renderer"in r){let a=e.renderers[r.name];a?e.renderers[r.name]=function(...o){let l=r.renderer.apply(this,o);return l===!1&&(l=a.apply(this,o)),l}:e.renderers[r.name]=r.renderer}if("tokenizer"in r){if(!r.level||r.level!=="block"&&r.level!=="inline")throw new Error("extension level must be 'block' or 'inline'");let a=e[r.level];a?a.unshift(r.tokenizer):e[r.level]=[r.tokenizer],r.start&&(r.level==="block"?e.startBlock?e.startBlock.push(r.start):e.startBlock=[r.start]:r.level==="inline"&&(e.startInline?e.startInline.push(r.start):e.startInline=[r.start]))}"childTokens"in r&&r.childTokens&&(e.childTokens[r.name]=r.childTokens)}),i.extensions=e),t.renderer){let r=this.defaults.renderer||new ro(this.defaults);for(let a in t.renderer){if(!(a in r))throw new Error(`renderer '${a}' does not exist`);if(["options","parser"].includes(a))continue;let o=a,l=t.renderer[o],c=r[o];r[o]=(...u)=>{let f=l.apply(r,u);return f===!1&&(f=c.apply(r,u)),f||""}}i.renderer=r}if(t.tokenizer){let r=this.defaults.tokenizer||new io(this.defaults);for(let a in t.tokenizer){if(!(a in r))throw new Error(`tokenizer '${a}' does not exist`);if(["options","rules","lexer"].includes(a))continue;let o=a,l=t.tokenizer[o],c=r[o];r[o]=(...u)=>{let f=l.apply(r,u);return f===!1&&(f=c.apply(r,u)),f}}i.tokenizer=r}if(t.hooks){let r=this.defaults.hooks||new Ua;for(let a in t.hooks){if(!(a in r))throw new Error(`hook '${a}' does not exist`);if(["options","block"].includes(a))continue;let o=a,l=t.hooks[o],c=r[o];Ua.passThroughHooks.has(a)?r[o]=u=>{if(this.defaults.async&&Ua.passThroughHooksRespectAsync.has(a))return(async()=>{let h=await l.call(r,u);return c.call(r,h)})();let f=l.call(r,u);return c.call(r,f)}:r[o]=(...u)=>{if(this.defaults.async)return(async()=>{let h=await l.apply(r,u);return h===!1&&(h=await c.apply(r,u)),h})();let f=l.apply(r,u);return f===!1&&(f=c.apply(r,u)),f}}i.hooks=r}if(t.walkTokens){let r=this.defaults.walkTokens,a=t.walkTokens;i.walkTokens=function(o){let l=[];return l.push(a.call(this,o)),r&&(l=l.concat(r.call(this,o))),l}}this.defaults={...this.defaults,...i}}),this}setOptions(n){return this.defaults={...this.defaults,...n},this}lexer(n,e){return Gn.lex(n,e??this.defaults)}parser(n,e){return Vn.parse(n,e??this.defaults)}parseMarkdown(n){return(e,t)=>{let i={...t},r={...this.defaults,...i},a=this.onError(!!r.silent,!!r.async);if(this.defaults.async===!0&&i.async===!1)return a(new Error("marked(): The async option was set to true by an extension. Remove async: false from the parse options object to return a Promise."));if(typeof e>"u"||e===null)return a(new Error("marked(): input parameter is undefined or null"));if(typeof e!="string")return a(new Error("marked(): input parameter is of type "+Object.prototype.toString.call(e)+", string expected"));if(r.hooks&&(r.hooks.options=r,r.hooks.block=n),r.async)return(async()=>{let o=r.hooks?await r.hooks.preprocess(e):e,l=await(r.hooks?await r.hooks.provideLexer(n):n?Gn.lex:Gn.lexInline)(o,r),c=r.hooks?await r.hooks.processAllTokens(l):l;r.walkTokens&&await Promise.all(this.walkTokens(c,r.walkTokens));let u=await(r.hooks?await r.hooks.provideParser(n):n?Vn.parse:Vn.parseInline)(c,r);return r.hooks?await r.hooks.postprocess(u):u})().catch(a);try{r.hooks&&(e=r.hooks.preprocess(e));let o=(r.hooks?r.hooks.provideLexer(n):n?Gn.lex:Gn.lexInline)(e,r);r.hooks&&(o=r.hooks.processAllTokens(o)),r.walkTokens&&this.walkTokens(o,r.walkTokens);let l=(r.hooks?r.hooks.provideParser(n):n?Vn.parse:Vn.parseInline)(o,r);return r.hooks&&(l=r.hooks.postprocess(l)),l}catch(o){return a(o)}}}onError(n,e){return t=>{if(t.message+=`
Please report this to https://github.com/markedjs/marked.`,n){let i="<p>An error occurred:</p><pre>"+ii(t.message+"",!0)+"</pre>";return e?Promise.resolve(i):i}if(e)return Promise.reject(t);throw t}}},xr=new np;function kt(n,e){return xr.parse(n,e)}kt.options=kt.setOptions=function(n){return xr.setOptions(n),kt.defaults=xr.defaults,Xh(kt.defaults),kt};kt.getDefaults=Oc;kt.defaults=wr;kt.use=function(...n){return xr.use(...n),kt.defaults=xr.defaults,Xh(kt.defaults),kt};kt.walkTokens=function(n,e){return xr.walkTokens(n,e)};kt.parseInline=xr.parseInline;kt.Parser=Vn;kt.parser=Vn.parse;kt.Renderer=ro;kt.TextRenderer=$c;kt.Lexer=Gn;kt.lexer=Gn.lex;kt.Tokenizer=io;kt.Hooks=Ua;kt.parse=kt;kt.options;kt.setOptions;kt.use;kt.walkTokens;kt.parseInline;Vn.parse;Gn.lex;Ft.registerLanguage("bash",hv);Ft.registerLanguage("css",yv);Ft.registerLanguage("diff",Ev);Ft.registerLanguage("dockerfile",Mv);Ft.registerLanguage("go",Tv);Ft.registerLanguage("ini",wv);Ft.registerLanguage("javascript",Nh);Ft.registerLanguage("js",Nh);Ft.registerLanguage("json",Nv);Ft.registerLanguage("markdown",Ph);Ft.registerLanguage("md",Ph);Ft.registerLanguage("python",Lh);Ft.registerLanguage("py",Lh);Ft.registerLanguage("rust",Dh);Ft.registerLanguage("rs",Dh);Ft.registerLanguage("shell",kh);Ft.registerLanguage("sh",kh);Ft.registerLanguage("sql",Pv);Ft.registerLanguage("typescript",Vh);Ft.registerLanguage("ts",Vh);Ft.registerLanguage("xml",Wh);Ft.registerLanguage("html",Wh);Ft.registerLanguage("yaml",$h);Ft.registerLanguage("yml",$h);const ip=new np({gfm:!0});function bx(n){return n.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;")}function Cd(n){return n.replace(/"/g,"&quot;").replace(/</g,"&lt;")}function Sx(n){return btoa(unescape(encodeURIComponent(n)))}ip.use({renderer:{code({text:n,lang:e}){const t=(e||"").toLowerCase(),i=t&&Ft.getLanguage(t);let r;try{r=i?Ft.highlight(n,{language:t,ignoreIllegals:!0}).value:Ft.highlightAuto(n).value}catch{r=bx(n)}const a=i?t:"text";return`<div class="code-block-wrap"><button class="code-copy-btn" type="button" data-clip-b64="${Sx(n)}" aria-label="Copy code">Copy</button><span class="code-lang">${Cd(a)}</span><pre class="hljs"><code class="hljs language-${Cd(a)}">${r}</code></pre></div>`}}});function Yn(n){const e=ip.parse(n,{async:!1});return v_.sanitize(e,{ADD_ATTR:["target","rel","data-clip-b64"],USE_PROFILES:{html:!0}})}function rs(n){const e=n.getAttribute("data-clip-b64");if(!e)return null;try{return decodeURIComponent(escape(atob(e)))}catch{return null}}const Nl=new Map;function rp(n){let e=Nl.get(n);return e||(e={messages:[],sessionId:null},Nl.set(n,e)),e}function yx(n,e){const t=rp(n);Object.assign(t,e)}Rc(n=>{Nl.delete(n)});const jn=_i("idle"),Id=_i(0),Bo=_i(!1),ap=_i(0),sp=_i([]);function Ex(n){sp.update(e=>{const t=[n,...e];return t.length>32?t.slice(0,32):t})}function Mx(){ap.update(n=>n+1)}var Tx=ie('<span class="text-muted text-xs italic"> </span>'),wx=ie('<div class="prose-chat leading-relaxed"></div>'),Ax=ie('<pre class="text-muted mt-1 whitespace-pre-wrap break-words"> </pre>'),Rx=ie('<p class="text-fg mt-1">result:</p> <pre class="text-muted whitespace-pre-wrap break-words"> </pre>',1),Cx=ie('<p class="text-err mt-1"> </p>'),Ix=ie('<div class="border border-border/40 rounded-wm p-2"><p class="font-mono text-accent"> </p> <!> <!> <!></div>'),Nx=ie('<details class="mt-2 text-xs"><summary class="text-muted cursor-pointer select-none"> </summary> <div class="mt-1 space-y-2"></div></details>'),Px=ie('<p class="mt-1 text-[10px] text-muted/70 font-mono"> </p>'),Lx=ie('<button class="opacity-0 group-hover:opacity-60 hover:!opacity-100 text-muted text-xs px-1 self-start transition-opacity" title="Copy message"> </button>'),Dx=ie('<div class="flex gap-3 group"><div class="w-12 shrink-0 text-xs font-mono uppercase opacity-60 pt-1"> </div> <div class="flex-1 min-w-0"><!> <!> <!> <!></div> <!></div>'),kx=ie('<div class="text-muted text-sm font-mono">Ask Zeus anything. Markdown + code blocks render inline; tool calls collapse into cards.</div>'),Ux=ie('<div class="h-full w-full flex flex-col" role="presentation"><div class="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-sm"></div> <form class="border-t border-border/40 p-2 flex gap-2"><textarea placeholder="Message Zeus…  ⏎ to send, Shift+⏎ for newline" class="flex-1 resize-none bg-transparent outline-none text-fg placeholder:text-muted/60 text-sm font-mono p-2" rows="1"></textarea> <button type="submit" class="px-3 py-1.5 rounded-md bg-accent text-bg text-sm font-mono disabled:opacity-40">Send</button></form></div>');function Xc(n,e){Mt(e,!1);let t=ft(e,"app",8);const i=rp(t().instanceId);let r=ue(i.messages),a=ue(i.sessionId),o=ue(""),l=ue(!1),c=ue(),u=ue(null);async function f(){const A=s(o).trim();if(!(!A||s(l))){W(l,!0),W(o,""),W(r,[...s(r),{role:"user",content:A},{role:"assistant",content:"",phase:"queued"}]),await vr(),h();try{await zg({message:A,sessionId:s(a),onPhase:k=>{Hn(r,s(r)[s(r).length-1].phase=k),W(r,s(r))},onToken:k=>{Hn(r,s(r)[s(r).length-1].content+=k),Hn(r,s(r)[s(r).length-1].phase=void 0),W(r,s(r)),h()},onDone:k=>{k.session_id&&W(a,k.session_id);const z=s(r)[s(r).length-1],H=k;Array.isArray(H.tool_calls)&&(z.toolCalls=H.tool_calls),typeof H.model_used=="string"&&(z.model=H.model_used),typeof H.latency_ms=="number"&&(z.latency_ms=H.latency_ms),W(r,s(r))},onError:k=>{Hn(r,s(r)[s(r).length-1].content=`**[error]** ${k}`),W(r,s(r)),mt({title:"Chat error",body:k.slice(0,140),kind:"err"})}})}finally{W(l,!1)}}}function h(){s(c)&&Hn(c,s(c).scrollTop=s(c).scrollHeight)}function d(A){A.key==="Enter"&&!A.shiftKey&&(A.preventDefault(),f())}function p(A){var z,H;const k=((z=s(r)[A])==null?void 0:z.content)??"";(H=navigator.clipboard)==null||H.writeText(k).then(()=>{W(u,A),setTimeout(()=>W(u,null),1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500}))}function m(A){var q;const k=A.target;if(!k)return;const z=k.closest(".code-copy-btn");if(!z)return;const H=rs(z);H!==null&&((q=navigator.clipboard)==null||q.writeText(H).then(()=>{const Q=z.textContent;z.textContent="Copied",z.classList.add("copied"),setTimeout(()=>{z.textContent=Q??"Copy",z.classList.remove("copied")},1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500})))}function E(A){if(A==null)return"";if(typeof A=="string")return A;try{return JSON.stringify(A,null,2)}catch{return String(A)}}const g=new Set;let _=!1;const O=sp.subscribe(A=>{if(!_){for(const k of A)g.add(k.id);_=!0;return}for(let k=A.length-1;k>=0;k--){const z=A[k];g.has(z.id)||(g.add(z.id),D(z))}});function D(A){const k=[];A.transcript&&k.push({role:"user",content:A.transcript}),A.reply&&k.push({role:"assistant",content:A.reply,model:A.model,latency_ms:void 0}),k.length&&(W(r,[...s(r),...k]),A.sessionId&&!s(a)&&W(a,A.sessionId),vr().then(h))}zt(()=>{}),Jt(()=>{O()}),lt(()=>(tt(t()),s(r),s(a)),()=>{yx(t().instanceId,{messages:s(r),sessionId:s(a)})}),Ht(),wt();var y=Ux(),B=M(y);ct(B,5,()=>s(r),$n,(A,k,z)=>{var H=Dx(),q=M(H),Q=M(q,!0);S(q);var G=U(q,2),T=M(G);{var w=N=>{var V=Tx(),re=M(V);S(V),me(()=>ee(re,`${s(k),L(()=>s(k).phase)??""}…`)),j(N,V)};Ae(T,N=>{s(k),L(()=>s(k).phase)&&N(w)})}var I=U(T,2);{var F=N=>{var V=wx();es(V,()=>(tt(Yn),s(k),L(()=>Yn(s(k).content))),!0),S(V),j(N,V)};Ae(I,N=>{s(k),L(()=>s(k).content)&&N(F)})}var Y=U(I,2);{var te=N=>{var V=Nx(),re=M(V),Me=M(re);S(re);var fe=U(re,2);ct(fe,5,()=>(s(k),L(()=>s(k).toolCalls)),$n,(oe,ve)=>{var ye=Ix(),Ie=M(ye),be=M(Ie,!0);S(Ie);var ke=U(Ie,2);{var xe=Oe=>{var J=Ax(),We=M(J,!0);S(J),me(Fe=>ee(We,Fe),[()=>(s(ve),L(()=>E(s(ve).arguments)))]),j(Oe,J)};Ae(ke,Oe=>{s(ve),L(()=>s(ve).arguments!==void 0)&&Oe(xe)})}var Ee=U(ke,2);{var _e=Oe=>{var J=Rx(),We=U(Pt(J),2),Fe=M(We,!0);S(We),me(P=>ee(Fe,P),[()=>(s(ve),L(()=>E(s(ve).result).slice(0,600)))]),j(Oe,J)};Ae(Ee,Oe=>{s(ve),L(()=>s(ve).result!==void 0)&&Oe(_e)})}var De=U(Ee,2);{var Ne=Oe=>{var J=Cx(),We=M(J,!0);S(J),me(()=>ee(We,(s(ve),L(()=>s(ve).error)))),j(Oe,J)};Ae(De,Oe=>{s(ve),L(()=>s(ve).error)&&Oe(Ne)})}S(ye),me(()=>ee(be,(s(ve),L(()=>s(ve).name??"unknown")))),j(oe,ye)}),S(fe),S(V),me(()=>ee(Me,`${s(k),L(()=>s(k).toolCalls.length)??""} tool call${s(k),L(()=>s(k).toolCalls.length===1?"":"s")??""}`)),j(N,V)};Ae(Y,N=>{s(k),L(()=>s(k).toolCalls&&s(k).toolCalls.length)&&N(te)})}var X=U(Y,2);{var K=N=>{var V=Px(),re=M(V);S(V),me(()=>ee(re,`${s(k),L(()=>s(k).model??"")??""}${s(k),L(()=>s(k).model&&s(k).latency_ms!==void 0?" · ":"")??""}${s(k),L(()=>s(k).latency_ms!==void 0?`${s(k).latency_ms}ms`:"")??""}`)),j(N,V)};Ae(X,N=>{s(k),L(()=>s(k).role==="assistant"&&(s(k).model||s(k).latency_ms!==void 0))&&N(K)})}S(G);var se=U(G,2);{var ne=N=>{var V=Lx(),re=M(V,!0);S(V),me(()=>ee(re,s(u)===z?"✓":"⧉")),Re("click",V,()=>p(z)),j(N,V)};Ae(se,N=>{s(k),L(()=>s(k).content)&&N(ne)})}S(H),me(()=>ee(Q,(s(k),L(()=>s(k).role==="user"?"you":"zeus")))),j(A,H)},A=>{var k=kx();j(A,k)}),S(B),Er(B,A=>W(c,A),()=>s(c));var R=U(B,2),C=M(R);fo(C);var b=U(C,2);S(R),S(y),me(A=>b.disabled=A,[()=>(s(l),s(o),L(()=>s(l)||!s(o).trim()))]),nn(C,()=>s(o),A=>W(o,A)),Re("keydown",C,d),Re("submit",R,lg(f)),Re("click",y,m),j(n,y),Tt()}function op(n){let e=null,t=!1,i=0;function r(){t||(e=new WebSocket(Nc("/zeus-os/sys/stream")),e.onmessage=a=>{try{n(JSON.parse(a.data))}catch{}},e.onclose=()=>{if(t)return;i+=1;const a=Math.min(5e3,500*2**Math.min(i,4));setTimeout(r,a)},e.onerror=()=>e==null?void 0:e.close())}return r(),{close(){t=!0,e==null||e.close()}}}var Ox=ie('<span class="text-fg"> </span>'),Fx=ie('<span class="text-muted">–</span>'),Bx=ie('<section class="mb-4"><header class="flex items-center justify-between mb-2"><h3 class="text-ok">GPU</h3> <span class="text-fg"> </span></header> <div class="text-muted text-xs"> </div></section>'),zx=ie('<section class="text-muted text-xs">GPU stats land in Phase 1.5 (nvidia-smi via host SSH). Until then, only container CPU + memory are sampled.</section>'),Hx=ie('<section class="mt-4 text-muted text-xs"> </section>'),Gx=ie('<div class="h-full w-full p-4 overflow-y-auto text-sm font-mono"><section class="mb-4"><header class="flex items-center justify-between mb-2"><h3 class="text-accent">CPU</h3> <span class="text-fg"> </span></header> <svg width="100%" height="42" viewBox="0 0 220 40" preserveAspectRatio="none" class="text-accent"><path fill="none" stroke="currentColor" stroke-width="1.5"></path></svg></section> <section class="mb-4"><header class="flex items-center justify-between mb-2"><h3 class="text-accent2">Memory</h3> <!></header> <svg width="100%" height="42" viewBox="0 0 220 40" preserveAspectRatio="none" class="text-accent2"><path fill="none" stroke="currentColor" stroke-width="1.5"></path></svg></section> <!> <!></div>');function qc(n,e){Mt(e,!1);const t=ue(),i=ue();ft(e,"app",8)();let a=ue(null),o=ue([]),l=ue([]),c=null;const u=60;function f(T,w){const I=T.slice(T.length>=u?1:0);return I.push(w??0),I}function h(T,w=220,I=40,F=100){if(T.length===0)return"";const Y=w/Math.max(1,u-1);return T.map((te,X)=>{const K=X*Y,se=I-te/F*I;return`${X===0?"M":"L"} ${K.toFixed(1)} ${se.toFixed(1)}`}).join(" ")}function d(T){if(T<1024)return`${T} B`;const w=["KB","MB","GB","TB"];let I=-1,F=T;for(;F>=1024&&I<w.length-1;)F/=1024,I+=1;return`${F.toFixed(1)} ${w[I]}`}zt(()=>{c=op(T=>{W(a,T),W(o,f(s(o),T.cpu_pct));const w=T.mem&&T.mem.total>0?(T.mem.total-T.mem.available)/T.mem.total*100:0;W(l,f(s(l),w))})}),Jt(()=>c==null?void 0:c.close()),lt(()=>s(o),()=>{W(t,h(s(o)))}),lt(()=>s(l),()=>{W(i,h(s(l)))}),Ht(),wt();var p=Gx(),m=M(p),E=M(m),g=U(M(E),2),_=M(g);S(g),S(E);var O=U(E,2),D=M(O);S(O),S(m);var y=U(m,2),B=M(y),R=U(M(B),2);{var C=T=>{var w=Ox(),I=M(w);S(w),me((F,Y)=>ee(I,`${F??""} / ${Y??""}`),[()=>(s(a),L(()=>d(s(a).mem.total-s(a).mem.available))),()=>(s(a),L(()=>d(s(a).mem.total)))]),j(T,w)},b=T=>{var w=Fx();j(T,w)};Ae(R,T=>{s(a),L(()=>{var w;return(w=s(a))==null?void 0:w.mem})?T(C):T(b,-1)})}S(B);var A=U(B,2),k=M(A);S(A),S(y);var z=U(y,2);{var H=T=>{var w=Bx(),I=M(w),F=U(M(I),2),Y=M(F);S(F),S(I);var te=U(I,2),X=M(te);S(te),S(w),me((K,se,ne,N)=>{ee(Y,`${K??""}% · ${se??""}°C`),ee(X,`VRAM ${ne??""} / ${N??""}`)},[()=>(s(a),L(()=>s(a).gpu.util.toFixed(0))),()=>(s(a),L(()=>s(a).gpu.temp_c.toFixed(0))),()=>(s(a),L(()=>d(s(a).gpu.mem_used))),()=>(s(a),L(()=>d(s(a).gpu.mem_total)))]),j(T,w)},q=T=>{var w=zx();j(T,w)};Ae(z,T=>{s(a),L(()=>{var w;return(w=s(a))==null?void 0:w.gpu})?T(H):T(q,-1)})}var Q=U(z,2);{var G=T=>{var w=Hx(),I=M(w);S(w),me(F=>ee(I,`Load average: ${F??""}`),[()=>(s(a),L(()=>s(a).load.map(F=>F.toFixed(2)).join(" · ")))]),j(T,w)};Ae(Q,T=>{s(a),L(()=>{var w;return(w=s(a))==null?void 0:w.load})&&T(G)})}S(p),me(T=>{ee(_,`${T??""}%`),$t(D,"d",s(t)),$t(k,"d",s(i))},[()=>(s(a),L(()=>{var T,w;return((w=(T=s(a))==null?void 0:T.cpu_pct)==null?void 0:w.toFixed(1))??"–"}))]),j(n,p),Tt()}function lp(){return dt("/zeus-os/fs/roots")}function cp(n){return dt(`/zeus-os/fs/list?path=${encodeURIComponent(n)}`)}function up(n){return dt(`/zeus-os/fs/file?path=${encodeURIComponent(n)}`)}var Vx=ie("<button> </button>"),Wx=ie('<div class="text-err px-3 py-2 text-xs"> </div>'),$x=ie('<li><button class="w-full text-left flex items-center justify-between px-3 py-1 hover:bg-surface2/60"><span class="truncate"> </span> <span class="text-muted text-xs"> </span></button></li>'),Xx=ie('<li class="px-3 py-2 text-muted text-xs">Empty directory.</li>'),qx=ie('<span class="text-warn text-[10px]">truncated</span>'),Yx=ie('<button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded hover:bg-accent hover:text-bg" title="Open in Editor">Edit</button>'),Kx=ie('<img class="max-w-full max-h-full object-contain"/>'),Zx=ie('<div class="prose-chat text-xs leading-relaxed" role="presentation"></div>'),Jx=ie('<header class="mb-2 text-accent flex items-center justify-between gap-2"><span class="truncate"> </span> <div class="flex gap-1 items-center"><!> <!></div></header> <!>',1),Qx=ie('<p class="text-muted">Select a file to preview. Markdown renders, code highlights, images show as thumbnails.</p>'),jx=ie('<div class="h-full w-full flex font-mono text-sm"><aside class="w-44 border-r border-border/40 overflow-y-auto p-2 space-y-1"><p class="text-xs text-muted px-2 pt-1 pb-2 uppercase">Roots</p> <!></aside> <div class="flex-1 flex flex-col min-w-0"><header class="flex items-center gap-2 px-3 py-1.5 border-b border-border/40 text-xs"><button class="text-muted hover:text-fg">↑</button> <span class="truncate"> </span></header> <!> <div class="flex-1 flex min-h-0"><ul class="w-1/2 overflow-y-auto border-r border-border/40"></ul> <div class="w-1/2 overflow-y-auto p-3 text-xs"><!></div></div></div></div>');function Yc(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue([]),a=ue(""),o=ue([]),l=ue(null),c=ue("");const u=new Set(["png","jpg","jpeg","gif","webp","svg","avif","ico"]),f=new Set(["md","markdown"]);async function h(){try{const F=await lp();console.log("[Zeus OS FileManager] roots response:",F),W(r,F.read_roots??[]),s(r).length&&!s(a)&&(W(a,s(r)[0]),await d(s(a)))}catch(F){W(c,String(F)),console.error("[Zeus OS FileManager] loadRoots error",F)}}async function d(F){W(c,""),W(l,null);try{const Y=await cp(F);W(a,Y.path),W(o,Y.entries)}catch(Y){W(c,String(Y)),W(o,[])}}function p(F){const Y=F.lastIndexOf(".");return Y<0?"":F.slice(Y+1).toLowerCase()}async function m(F){const Y=s(a).endsWith("/")?s(a)+F.name:s(a)+"/"+F.name;if(F.kind==="dir"){await d(Y);return}if(F.kind!=="file")return;const te=p(F.name);if(u.has(te))try{const X=await fetch(`/zeus-os/fs/raw?path=${encodeURIComponent(Y)}`);if(X.ok){const K=await X.blob(),se=URL.createObjectURL(K);W(l,{name:F.name,absPath:Y,kind:"image",content:"",src:se});return}}catch{}try{const X=await up(Y),K=f.has(te)?"markdown":"text";W(l,{name:F.name,absPath:Y,kind:K,content:X.content,truncated:X.truncated})}catch(X){W(c,String(X))}}function E(){const F=s(a).replace(/\/+$/,"").split("/");if(F.length<=1)return;F.pop();const Y=F.join("/")||"/";d(Y)}function g(F){if(F<1024)return`${F} B`;const Y=["KB","MB","GB"];let te=-1,X=F;for(;X>=1024&&te<Y.length-1;)X/=1024,te+=1;return`${X.toFixed(1)} ${Y[te]}`}function _(F){const Y=p(F);return{py:"python",ts:"typescript",tsx:"typescript",js:"javascript",jsx:"javascript",svelte:"xml",html:"xml",xml:"xml",json:"json",yaml:"yaml",yml:"yaml",sh:"bash",bash:"bash",zsh:"bash",css:"css",go:"go",rs:"rust",sql:"sql",md:"markdown",ini:"ini",toml:"ini",dockerfile:"dockerfile"}[Y]??""}zt(h);function O(F){var K;const Y=F.target;if(!Y)return;const te=Y.closest(".code-copy-btn");if(!te)return;const X=rs(te);X!==null&&((K=navigator.clipboard)==null||K.writeText(X).then(()=>{const se=te.textContent;te.textContent="Copied",te.classList.add("copied"),setTimeout(()=>{te.textContent=se??"Copy",te.classList.remove("copied")},1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500})))}lt(()=>(s(l),Yn),()=>{W(t,(()=>{if(!s(l))return"";if(s(l).kind==="markdown")return Yn(s(l).content);if(s(l).kind==="text"){const Y="```"+_(s(l).name)+`
`+s(l).content+"\n```";return Yn(Y)}return""})())}),Ht(),wt();var D=jx(),y=M(D),B=U(M(y),2);ct(B,1,()=>s(r),F=>F,(F,Y)=>{var te=Vx();let X;var K=M(te,!0);S(te),me(()=>{X=vt(te,1,"w-full text-left px-2 py-1 rounded hover:bg-surface2/60 truncate",null,X,{"bg-surface2":s(Y)===s(a)}),$t(te,"title",s(Y)),ee(K,s(Y))}),Re("click",te,()=>d(s(Y))),j(F,te)}),S(y);var R=U(y,2),C=M(R),b=M(C),A=U(b,2),k=M(A,!0);S(A),S(C);var z=U(C,2);{var H=F=>{var Y=Wx(),te=M(Y,!0);S(Y),me(()=>ee(te,s(c))),j(F,Y)};Ae(z,F=>{s(c)&&F(H)})}var q=U(z,2),Q=M(q);ct(Q,5,()=>s(o),F=>F.name,(F,Y)=>{var te=$x(),X=M(te),K=M(X),se=M(K);S(K);var ne=U(K,2),N=M(ne,!0);S(ne),S(X),S(te),me(V=>{ee(se,`${s(Y),L(()=>s(Y).kind==="dir"?"📁":s(Y).kind==="link"?"🔗":"📄")??""}
                 ${s(Y),L(()=>s(Y).name)??""}`),ee(N,V)},[()=>(s(Y),L(()=>s(Y).kind==="dir"?"":g(s(Y).size)))]),Re("dblclick",X,()=>m(s(Y))),Re("click",X,()=>m(s(Y))),j(F,te)},F=>{var Y=Xx();j(F,Y)}),S(Q);var G=U(Q,2),T=M(G);{var w=F=>{var Y=Jx(),te=Pt(Y),X=M(te),K=M(X,!0);S(X);var se=U(X,2),ne=M(se);{var N=ve=>{var ye=qx();j(ve,ye)};Ae(ne,ve=>{s(l),L(()=>s(l).truncated)&&ve(N)})}var V=U(ne,2);{var re=ve=>{var ye=Yx();Re("click",ye,()=>gr({appId:"editor",kind:"Editor",title:s(l).name,props:{path:s(l).absPath}})),j(ve,ye)};Ae(V,ve=>{s(l),L(()=>s(l).kind!=="image")&&ve(re)})}S(se),S(te);var Me=U(te,2);{var fe=ve=>{var ye=Kx();me(()=>{$t(ye,"src",(s(l),L(()=>s(l).src))),$t(ye,"alt",(s(l),L(()=>s(l).name)))}),j(ve,ye)},oe=ve=>{var ye=Zx();es(ye,()=>s(t),!0),S(ye),Re("click",ye,O),j(ve,ye)};Ae(Me,ve=>{s(l),L(()=>s(l).kind==="image"&&s(l).src)?ve(fe):ve(oe,-1)})}me(()=>ee(K,(s(l),L(()=>s(l).name)))),j(F,Y)},I=F=>{var Y=Qx();j(F,Y)};Ae(T,F=>{s(l)?F(w):F(I,-1)})}S(G),S(q),S(R),S(D),me(()=>ee(k,s(a)||"–")),Re("click",b,E),j(n,D),Tt()}function e0(){return dt("/admin/tools")}function t0(n={}){const e=new URLSearchParams;n.limit&&e.set("limit",String(n.limit)),n.tool&&e.set("tool",n.tool);const t=e.toString();return dt(`/admin/tools/invocations${t?"?"+t:""}`)}var n0=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"><strong>Error fetching tools:</strong> </div>'),i0=ie('<span class="text-accent2" title="Registration surfaces"> </span>'),r0=ie('<span class="text-ok">cache</span>'),a0=ie('<span title="Aegis policy"> </span>'),s0=ie("<span> </span>"),o0=ie('<li><button><div class="text-fg"> </div> <div class="text-muted text-[10px] truncate"> </div> <div class="flex gap-1 mt-1 text-[10px] text-muted flex-wrap"><!> <!> <!> <!></div></button></li>'),l0=ie('<details class="mt-2"><summary class="text-muted cursor-pointer">parameters schema</summary> <pre class="mt-1 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto"> </pre></details>'),c0=ie('<div class="p-3 border-b border-border/40"><header class="flex items-center justify-between mb-1"><h3 class="text-accent text-sm"> </h3> <button class="text-muted hover:text-fg text-[10px]"> </button></header> <p class="text-muted leading-relaxed"> </p> <!></div>'),u0=ie('· filter: <span class="text-fg"> </span>',1),d0=ie('<p class="text-err px-3 py-2"> </p>'),f0=ie('<span class="text-ok ml-2">cache</span>'),h0=ie('<span class="text-err ml-2">aegis</span>'),p0=ie('<span class="text-err ml-2">err</span>'),m0=ie('<span class="ml-2"> </span>'),g0=ie('<pre class="mt-1 text-[10px] text-muted whitespace-pre-wrap break-words"> </pre>'),_0=ie('<pre class="mt-1 text-[10px] text-fg/80 whitespace-pre-wrap break-words"> </pre>'),v0=ie('<li class="px-3 py-2 border-b border-border/20 hover:bg-surface2/40"><header class="flex items-center justify-between text-[10px] text-muted"><span><span class="text-fg"> </span> <!> <!> <!> <!></span> <span> </span></header> <!> <!></li>'),x0=ie('<li class="px-3 py-6 text-muted text-center">No invocations recorded yet. Ask Zeus a tool-worthy question to populate this feed.</li>'),b0=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <div class="flex-1 flex min-h-0"><aside class="w-72 border-r border-border/40 flex flex-col"><header class="px-3 py-2 border-b border-border/40 flex items-center justify-between"><div><h3 class="text-accent text-sm">Tools</h3> <p class="text-muted text-[10px]"> <!></p></div> <input placeholder="filter…" class="bg-transparent border-b border-border/40 text-fg outline-none text-[11px] w-24"/></header> <ul class="flex-1 overflow-y-auto"></ul></aside> <section class="flex-1 flex flex-col min-w-0"><!> <div class="px-3 py-2 border-b border-border/40 flex items-center justify-between"><h3 class="text-accent text-sm">Recent invocations</h3> <span class="text-muted text-[10px]"> <!></span></div> <!> <ul class="flex-1 overflow-y-auto"></ul></section></div></div>');function Kc(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue([]),a=ue(),o=ue([]),l=ue(""),c=ue(""),u=ue(""),f=ue(!0),h=ue(""),d=null,p=ue(null);async function m(){try{W(f,!0);const[N,V]=await Promise.all([e0(),t0({limit:100,tool:s(c)||void 0})]),re=N,Me=Array.isArray(re.tools)?re.tools:Array.isArray(N)?N:[],fe=new Map;for(const oe of Me){const ve=oe.name,ye=fe.get(ve);ye?oe.source&&!(ye.sources??[]).includes(oe.source)&&(ye.sources=[...ye.sources??[],oe.source]):fe.set(ve,{...oe,sources:oe.source?[oe.source]:[]})}W(r,[...fe.values()]),W(a,N.tools_enabled),W(o,V.invocations??[]),W(u,""),W(h,new Date().toLocaleTimeString()),console.log("[Zeus OS Tools] got",s(r).length,"tools, first 3:",s(r).slice(0,3).map(oe=>oe==null?void 0:oe.name))}catch(N){W(u,String(N)),console.error("[Zeus OS Tools] refresh error",N)}finally{W(f,!1)}}zt(()=>{m(),d=setInterval(m,4e3)}),Jt(()=>{d&&clearInterval(d)});function E(N,V){const re=V.toLowerCase().trim();return re?N.filter(Me=>(Me.name??"").toLowerCase().includes(re)||(Me.description??"").toLowerCase().includes(re)):N}function g(N){try{return new Date(N).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"})}catch{return N}}function _(N){if(!N||Object.keys(N).length===0)return"";try{return JSON.stringify(N)}catch{return""}}lt(()=>(s(r),s(l)),()=>{W(t,E(s(r),s(l)))}),Ht(),wt();var O=b0(),D=M(O);{var y=N=>{var V=n0(),re=U(M(V));S(V),me(()=>ee(re,` ${s(u)??""}`)),j(N,V)};Ae(D,N=>{s(u)&&N(y)})}var B=U(D,2),R=M(B),C=M(R),b=M(C),A=U(M(b),2),k=M(A),z=U(k);{var H=N=>{var V=ea();me(()=>ee(V,`· ${s(h)??""}`)),j(N,V)};Ae(z,N=>{s(h)&&N(H)})}S(A),S(b);var q=U(b,2);gn(q),S(C);var Q=U(C,2);ct(Q,5,()=>s(t),N=>N.name,(N,V)=>{var re=o0(),Me=M(re);let fe;var oe=M(Me),ve=M(oe,!0);S(oe);var ye=U(oe,2),Ie=M(ye);S(ye);var be=U(ye,2),ke=M(be);{var xe=We=>{var Fe=i0(),P=M(Fe,!0);S(Fe),me(x=>ee(P,x),[()=>(s(V),L(()=>s(V).sources.join("+")))]),j(We,Fe)};Ae(ke,We=>{s(V),L(()=>s(V).sources&&s(V).sources.length)&&We(xe)})}var Ee=U(ke,2);{var _e=We=>{var Fe=r0();j(We,Fe)};Ae(Ee,We=>{s(V),L(()=>s(V).cacheable)&&We(_e)})}var De=U(Ee,2);{var Ne=We=>{var Fe=a0(),P=M(Fe,!0);S(Fe),me(()=>ee(P,(s(V),L(()=>s(V).aegis_policy)))),j(We,Fe)};Ae(De,We=>{s(V),L(()=>s(V).aegis_policy)&&We(Ne)})}var Oe=U(De,2);{var J=We=>{var Fe=s0(),P=M(Fe);S(Fe),me(()=>ee(P,`${s(V),L(()=>s(V).timeout_seconds)??""}s`)),j(We,Fe)};Ae(Oe,We=>{s(V),L(()=>s(V).timeout_seconds)&&We(J)})}S(be),S(Me),S(re),me(We=>{var Fe;fe=vt(Me,1,"w-full text-left px-3 py-2 hover:bg-surface2/60",null,fe,{"bg-surface2":((Fe=s(p))==null?void 0:Fe.name)===s(V).name}),ee(ve,(s(V),L(()=>s(V).name))),ee(Ie,`${We??""}…`)},[()=>(s(V),L(()=>s(V).description.slice(0,60)))]),Re("click",Me,()=>W(p,s(V))),j(N,re)}),S(Q),S(R);var G=U(R,2),T=M(G);{var w=N=>{var V=c0(),re=M(V),Me=M(re),fe=M(Me,!0);S(Me);var oe=U(Me,2),ve=M(oe,!0);S(oe),S(re);var ye=U(re,2),Ie=M(ye,!0);S(ye);var be=U(ye,2);{var ke=xe=>{var Ee=l0(),_e=U(M(Ee),2),De=M(_e,!0);S(_e),S(Ee),me(Ne=>ee(De,Ne),[()=>(s(p),L(()=>JSON.stringify(s(p).parameters,null,2)))]),j(xe,Ee)};Ae(be,xe=>{s(p),L(()=>s(p).parameters)&&xe(ke)})}S(V),me(()=>{ee(fe,(s(p),L(()=>s(p).name))),ee(ve,(s(c),s(p),L(()=>s(c)===s(p).name?"Show all":"Filter feed"))),ee(Ie,(s(p),L(()=>s(p).description)))}),Re("click",oe,()=>{W(c,s(c)===s(p).name?"":s(p).name),m()}),j(N,V)};Ae(T,N=>{s(p)&&N(w)})}var I=U(T,2),F=U(M(I),2),Y=M(F),te=U(Y);{var X=N=>{var V=u0(),re=U(Pt(V)),Me=M(re,!0);S(re),me(()=>ee(Me,s(c))),j(N,V)};Ae(te,N=>{s(c)&&N(X)})}S(F),S(I);var K=U(I,2);{var se=N=>{var V=d0(),re=M(V,!0);S(V),me(()=>ee(re,s(u))),j(N,V)};Ae(K,N=>{s(u)&&N(se)})}var ne=U(K,2);ct(ne,5,()=>s(o),$n,(N,V)=>{var re=v0(),Me=M(re),fe=M(Me),oe=M(fe),ve=M(oe,!0);S(oe);var ye=U(oe,2);{var Ie=Z=>{var ae=f0();j(Z,ae)};Ae(ye,Z=>{s(V),L(()=>s(V).cache_hit)&&Z(Ie)})}var be=U(ye,2);{var ke=Z=>{var ae=h0();j(Z,ae)};Ae(be,Z=>{s(V),L(()=>s(V).aegis_rejected)&&Z(ke)})}var xe=U(be,2);{var Ee=Z=>{var ae=p0();j(Z,ae)};Ae(xe,Z=>{s(V),L(()=>s(V).is_error)&&Z(Ee)})}var _e=U(xe,2);{var De=Z=>{var ae=m0(),de=M(ae,!0);S(ae),me(()=>ee(de,(s(V),L(()=>s(V).source)))),j(Z,ae)};Ae(_e,Z=>{s(V),L(()=>s(V).source)&&Z(De)})}S(fe);var Ne=U(fe,2),Oe=M(Ne);S(Ne),S(Me);var J=U(Me,2);{var We=Z=>{var ae=g0(),de=M(ae,!0);S(ae),me(Le=>ee(de,Le),[()=>(s(V),L(()=>_(s(V).args)))]),j(Z,ae)},Fe=nr(()=>(s(V),L(()=>_(s(V).args))));Ae(J,Z=>{s(Fe)&&Z(We)})}var P=U(J,2);{var x=Z=>{var ae=_0(),de=M(ae);S(ae),me(Le=>ee(de,`${Le??""}${s(V),L(()=>s(V).content.length>240?"…":"")??""}`),[()=>(s(V),L(()=>s(V).content.slice(0,240)))]),j(Z,ae)};Ae(P,Z=>{s(V),L(()=>s(V).content)&&Z(x)})}S(re),me(Z=>{ee(ve,(s(V),L(()=>s(V).tool))),ee(Oe,`${Z??""}${s(V),L(()=>s(V).duration_ms?` · ${s(V).duration_ms}ms`:"")??""}`)},[()=>(s(V),L(()=>g(s(V).ts)))]),j(N,re)},N=>{var V=x0();j(N,V)}),S(ne),S(G),S(B),S(O),me(()=>{ee(k,`${s(f),s(r),L(()=>s(f)&&s(r).length===0?"loading…":`${s(r).length} registered`)??""}${s(a)===!1?" · loop disabled":""} `),ee(Y,`${s(o),L(()=>s(o).length)??""} shown `)}),nn(q,()=>s(l),N=>W(l,N)),j(n,O),Tt()}function S0(){return dt("/kronos/jobs")}function y0(n){return dt(`/kronos/jobs/${encodeURIComponent(n)}`)}function E0(){return dt("/kronos/executors")}function M0(){return dt("/kronos/schedule/upcoming")}function T0(n){return dt("/kronos/jobs",{method:"POST",body:JSON.stringify(n)})}function w0(n){return dt(`/kronos/jobs/${encodeURIComponent(n)}`,{method:"DELETE"})}function A0(n){return dt(`/kronos/jobs/${encodeURIComponent(n)}/run`,{method:"POST"})}function R0(n,e){const t=e?"enable":"disable";return dt(`/kronos/jobs/${encodeURIComponent(n)}/${t}`,{method:"POST"})}var C0=ie("<option> </option>"),I0=ie('<form class="px-3 py-3 border-b border-border/40 space-y-2 bg-surface2/30"><input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" placeholder="job id (slug)" required=""/> <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" placeholder="display name"/> <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" placeholder="cron (e.g. 0 7 * * *)"/> <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" placeholder="run_at (ISO; one-off)"/> <select class="w-full bg-surface text-fg p-1 rounded outline-none border border-border/40" required=""><option>executor…</option><!></select> <textarea class="w-full bg-transparent border border-border/40 rounded p-1 text-fg outline-none" rows="3" placeholder="args JSON, e.g. {&quot;topic&quot;: &quot;...&quot;}"></textarea> <button type="submit" class="w-full bg-accent text-bg py-1 rounded text-[11px]">Create</button></form>'),N0=ie('<li><button><div class="flex items-center justify-between"><span class="text-fg truncate"> </span> <span> </span></div> <div class="text-muted text-[10px] truncate"> </div></button></li>'),P0=ie('<li class="px-3 py-4 text-muted text-center">No jobs.</li>'),L0=ie('<p class="text-[11px] text-fg/80"><span class="text-muted"> </span> </p>'),D0=ie('<div class="border-t border-border/40 px-3 py-2 max-h-32 overflow-y-auto"><p class="text-[10px] text-muted uppercase mb-1">Upcoming</p> <!></div>'),k0=ie('<p class="text-err px-3 py-2 text-[11px]"> </p>'),U0=ie('<p class="text-fg/80 text-[11px] mt-1"> </p>'),O0=ie('<details class="mt-1"><summary class="text-muted text-[10px] cursor-pointer">params</summary> <pre class="mt-1 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto"> </pre></details>'),F0=ie('<p class="text-err text-[11px] mt-1"> </p>'),B0=ie('<pre class="text-[10px] text-fg/80 whitespace-pre-wrap mt-1"> </pre>'),z0=ie('<li class="px-3 py-2 border-b border-border/20"><header class="flex items-center justify-between text-[10px] text-muted"><span><span class="text-fg"> </span> <!> <!></span> <span> </span></header> <!> <!></li>'),H0=ie('<li class="px-3 py-4 text-muted text-center">No runs yet.</li>'),G0=ie('<header class="px-3 py-2 border-b border-border/40"><div class="flex items-center justify-between"><h3 class="text-accent text-sm"> </h3> <div class="flex gap-1"><button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded">Run now</button> <button class="text-[10px] px-2 py-0.5 border border-border/60 text-fg rounded"> </button> <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded">Delete</button></div></div> <p class="text-muted text-[10px] mt-1"> </p> <!> <p class="text-muted text-[10px] mt-1"> </p> <!></header> <div class="px-3 py-2 border-b border-border/40 text-[11px] text-accent">Runs</div> <ul class="flex-1 overflow-y-auto"></ul>',1),V0=ie('<div class="flex-1 grid place-items-center text-muted text-center px-6"><div><p>Pick a job to see its run history,</p> <p>or hit <span class="text-accent">+ New</span> to create one.</p> <p class="mt-3 text-[10px]">Jobs created via Zeus chat appear here automatically.</p></div></div>'),W0=ie('<div class="h-full w-full flex font-mono text-xs"><aside class="w-72 border-r border-border/40 flex flex-col"><header class="px-3 py-2 border-b border-border/40 flex items-center justify-between"><div><h3 class="text-accent text-sm">Kronos jobs</h3> <p class="text-muted text-[10px]"> </p></div> <button class="text-[10px] px-2 py-0.5 rounded border border-accent text-accent hover:bg-accent hover:text-bg"> </button></header> <!> <ul class="flex-1 overflow-y-auto"></ul> <!></aside> <section class="flex-1 flex flex-col min-w-0"><!> <!></section></div>');function Zc(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue([]),a=ue([]),o=ue([]),l=ue([]),c=ue(null),u=ue(""),f=null,h=ue(!1),d=ue({id:"",name:"",cron:"",run_at:"",executor:"",args_json:"{}"});async function p(){try{const[ne,N]=await Promise.all([S0(),M0()]);W(r,Array.isArray(ne)?ne:[]),W(a,Array.isArray(N)?N:[]),W(u,"")}catch(ne){W(u,String(ne))}}async function m(){if(s(c))try{const ne=await y0(s(c));W(l,ne.runs??[])}catch(ne){W(u,String(ne))}}async function E(){try{W(o,await E0())}catch{W(o,[])}}function g(ne){W(c,ne),m()}async function _(ne){ne.preventDefault();let N={};try{N=JSON.parse(s(d).args_json||"{}")}catch{mt({title:"Params JSON invalid",kind:"err"});return}if(!s(d).id||!s(d).executor){mt({title:"Need at least id + executor",kind:"warn"});return}if(!s(d).cron&&!s(d).run_at){mt({title:"Need cron OR run_at",kind:"warn"});return}try{const V=await T0({id:s(d).id,name:s(d).name||s(d).id,schedule:{cron:s(d).cron||null,timezone:"UTC",run_at:s(d).run_at||null},executor:s(d).executor,params:N,enabled:!0});mt({title:"Job created",body:V.id,kind:"ok"}),W(h,!1),W(d,{id:"",name:"",cron:"",run_at:"",executor:"",args_json:"{}"}),await p(),W(c,V.id),await m()}catch(V){mt({title:"Create failed",body:String(V).slice(0,200),kind:"err"})}}async function O(ne){try{await A0(ne),mt({title:"Triggered",body:ne,kind:"ok",ttlMs:1800}),await m()}catch(N){mt({title:"Run failed",body:String(N).slice(0,160),kind:"err"})}}async function D(ne){try{await R0(ne.id,!ne.enabled),await p()}catch(N){mt({title:"Toggle failed",body:String(N).slice(0,160),kind:"err"})}}async function y(ne){if(confirm(`Delete job '${ne.id}'?`))try{await w0(ne.id),s(c)===ne.id&&W(c,null),await p()}catch(N){mt({title:"Delete failed",body:String(N).slice(0,160),kind:"err"})}}function B(ne){if(!ne)return"–";try{return new Date(ne).toLocaleString([],{dateStyle:"short",timeStyle:"short"})}catch{return ne}}zt(()=>{p(),E(),f=setInterval(()=>{p(),s(c)&&m()},6e3)}),Jt(()=>{f&&clearInterval(f)}),lt(()=>(s(r),s(c)),()=>{W(t,s(r).find(ne=>ne.id===s(c))??null)}),Ht(),wt();var R=W0(),C=M(R),b=M(C),A=M(b),k=U(M(A),2),z=M(k);S(k),S(A);var H=U(A,2),q=M(H,!0);S(H),S(b);var Q=U(b,2);{var G=ne=>{var N=I0(),V=M(N);gn(V);var re=U(V,2);gn(re);var Me=U(re,2);gn(Me);var fe=U(Me,2);gn(fe);var oe=U(fe,2),ve=M(oe);ve.value=ve.__value="";var ye=U(ve);ct(ye,1,()=>s(o),be=>be.dotted_path,(be,ke)=>{var xe=C0(),Ee=M(xe,!0);S(xe);var _e={};me(()=>{ee(Ee,(s(ke),L(()=>s(ke).dotted_path))),_e!==(_e=(s(ke),L(()=>s(ke).dotted_path)))&&(xe.value=(xe.__value=(s(ke),L(()=>s(ke).dotted_path)))??"")}),j(be,xe)}),S(oe);var Ie=U(oe,2);fo(Ie),kn(2),S(N),nn(V,()=>s(d).id,be=>(Hn(d,s(d).id=be),Nr(()=>{s(o)}))),nn(re,()=>s(d).name,be=>(Hn(d,s(d).name=be),Nr(()=>{s(o)}))),nn(Me,()=>s(d).cron,be=>(Hn(d,s(d).cron=be),Nr(()=>{s(o)}))),nn(fe,()=>s(d).run_at,be=>(Hn(d,s(d).run_at=be),Nr(()=>{s(o)}))),Ni(oe,()=>s(d).executor,be=>(Hn(d,s(d).executor=be),Nr(()=>{s(o)}))),nn(Ie,()=>s(d).args_json,be=>(Hn(d,s(d).args_json=be),Nr(()=>{s(o)}))),Re("submit",N,_),j(ne,N)};Ae(Q,ne=>{s(h)&&ne(G)})}var T=U(Q,2);ct(T,5,()=>s(r),ne=>ne.id,(ne,N)=>{var V=N0(),re=M(V);let Me;var fe=M(re),oe=M(fe),ve=M(oe,!0);S(oe);var ye=U(oe,2),Ie=M(ye,!0);S(ye),S(fe);var be=U(fe,2),ke=M(be,!0);S(be),S(re),S(V),me(()=>{Me=vt(re,1,"w-full text-left px-3 py-2 hover:bg-surface2/60",null,Me,{"bg-surface2":s(c)===s(N).id}),ee(ve,(s(N),L(()=>s(N).name||s(N).id))),vt(ye,1,`text-[10px] ${s(N),L(()=>s(N).enabled?"text-ok":"text-muted")??""}`),ee(Ie,(s(N),L(()=>s(N).enabled?"on":"off"))),ee(ke,(s(N),L(()=>{var xe,Ee;return((xe=s(N).schedule)==null?void 0:xe.cron)||((Ee=s(N).schedule)==null?void 0:Ee.run_at)||"–"})))}),Re("click",re,()=>g(s(N).id)),j(ne,V)},ne=>{var N=P0();j(ne,N)}),S(T);var w=U(T,2);{var I=ne=>{var N=D0(),V=U(M(N),2);ct(V,1,()=>(s(a),L(()=>s(a).slice(0,5))),$n,(re,Me)=>{var fe=L0(),oe=M(fe),ve=M(oe,!0);S(oe);var ye=U(oe);S(fe),me(Ie=>{ee(ve,Ie),ee(ye,` ${s(Me),L(()=>s(Me).name||s(Me).job_id)??""}`)},[()=>(s(Me),L(()=>B(s(Me).next_fire)))]),j(re,fe)}),S(N),j(ne,N)};Ae(w,ne=>{s(a),L(()=>s(a).length>0)&&ne(I)})}S(C);var F=U(C,2),Y=M(F);{var te=ne=>{var N=k0(),V=M(N,!0);S(N),me(()=>ee(V,s(u))),j(ne,N)};Ae(Y,ne=>{s(u)&&ne(te)})}var X=U(Y,2);{var K=ne=>{var N=G0(),V=Pt(N),re=M(V),Me=M(re),fe=M(Me,!0);S(Me);var oe=U(Me,2),ve=M(oe),ye=U(ve,2),Ie=M(ye,!0);S(ye);var be=U(ye,2);S(oe),S(re);var ke=U(re,2),xe=M(ke);S(ke);var Ee=U(ke,2);{var _e=P=>{var x=U0(),Z=M(x,!0);S(x),me(()=>ee(Z,(s(t),L(()=>s(t).description)))),j(P,x)};Ae(Ee,P=>{s(t),L(()=>s(t).description)&&P(_e)})}var De=U(Ee,2),Ne=M(De);S(De);var Oe=U(De,2);{var J=P=>{var x=O0(),Z=U(M(x),2),ae=M(Z,!0);S(Z),S(x),me(de=>ee(ae,de),[()=>(s(t),L(()=>JSON.stringify(s(t).params,null,2)))]),j(P,x)},We=nr(()=>(s(t),L(()=>s(t).params&&Object.keys(s(t).params).length)));Ae(Oe,P=>{s(We)&&P(J)})}S(V);var Fe=U(V,4);ct(Fe,5,()=>s(l),P=>P.id,(P,x)=>{var Z=z0(),ae=M(Z),de=M(ae),Le=M(de),He=M(Le,!0);S(Le);var Se=U(Le,2);{var we=Be=>{var Te=ea();me(Ve=>ee(Te,`· ${Ve??""}ms`),[()=>(s(x),L(()=>Math.round(s(x).duration_ms)))]),j(Be,Te)};Ae(Se,Be=>{s(x),L(()=>s(x).duration_ms)&&Be(we)})}var Ge=U(Se,2);{var Je=Be=>{var Te=ea();me(()=>ee(Te,`· attempt ${s(x),L(()=>s(x).attempts)??""}`)),j(Be,Te)};Ae(Ge,Be=>{s(x),L(()=>s(x).attempts&&s(x).attempts>1)&&Be(Je)})}S(de);var Pe=U(de,2),Ce=M(Pe,!0);S(Pe),S(ae);var qe=U(ae,2);{var je=Be=>{var Te=F0(),Ve=M(Te,!0);S(Te),me(()=>ee(Ve,(s(x),L(()=>s(x).error)))),j(Be,Te)};Ae(qe,Be=>{s(x),L(()=>s(x).error)&&Be(je)})}var st=U(qe,2);{var ce=Be=>{var Te=B0(),Ve=M(Te);S(Te),me(Ye=>ee(Ve,`${Ye??""}${s(x),L(()=>s(x).output_summary.length>300?"…":"")??""}`),[()=>(s(x),L(()=>s(x).output_summary.slice(0,300)))]),j(Be,Te)};Ae(st,Be=>{s(x),L(()=>s(x).output_summary)&&Be(ce)})}S(Z),me(Be=>{ee(He,(s(x),L(()=>s(x).status))),ee(Ce,Be)},[()=>(s(x),L(()=>B(s(x).finished_at||s(x).started_at)))]),j(P,Z)},P=>{var x=H0();j(P,x)}),S(Fe),me(P=>{ee(fe,(s(t),L(()=>s(t).name||s(t).id))),ee(Ie,(s(t),L(()=>s(t).enabled?"Disable":"Enable"))),ee(xe,`${s(t),L(()=>s(t).id)??""} · ${s(t),L(()=>s(t).executor||s(t).agent||"(no executor)")??""}`),ee(Ne,`${s(t),L(()=>{var x;return(x=s(t).schedule)!=null&&x.cron?`cron: ${s(t).schedule.cron}`:""})??""}
          ${s(t),L(()=>{var x;return(x=s(t).schedule)!=null&&x.run_at?` run_at: ${s(t).schedule.run_at}`:""})??""}
          ${s(t),L(()=>{var x;return(x=s(t).schedule)!=null&&x.timezone?` (${s(t).schedule.timezone})`:""})??""}
          · last: ${P??""}`)},[()=>(s(t),L(()=>B(s(t).last_fired_at)))]),Re("click",ve,()=>O(s(t).id)),Re("click",ye,()=>D(s(t))),Re("click",be,()=>y(s(t))),j(ne,N)},se=ne=>{var N=V0();j(ne,N)};Ae(X,ne=>{s(t)?ne(K):ne(se,-1)})}S(F),S(R),me(()=>{ee(z,`${s(r),L(()=>s(r).length)??""} registered`),ee(q,s(h)?"Cancel":"+ New")}),Re("click",H,()=>W(h,!s(h))),j(n,R),Tt()}function $0(n={}){const e=new URLSearchParams;n.bucket&&e.set("bucket",n.bucket),n.since_days&&e.set("since_days",String(n.since_days)),n.provider&&e.set("provider",n.provider),n.caller&&e.set("caller",n.caller);const t=e.toString();return dt(`/admin/llm_usage${t?"?"+t:""}`)}function Nd(){return dt("/admin/llm_usage/import",{method:"POST"})}var X0=ie('<div class="bg-surface2/40 rounded p-3"><p class="text-muted text-[10px] uppercase"> </p> <p class="text-fg text-xl"> </p> <p class="text-muted text-[10px]"> </p></div> <div class="bg-surface2/40 rounded p-3"><p class="text-muted text-[10px] uppercase"> </p> <p class="text-fg text-xl"> </p> <p class="text-muted text-[10px]"> </p></div> <div class="bg-surface2/40 rounded p-3"><p class="text-muted text-[10px] uppercase">Top provider</p> <p class="text-fg text-sm truncate"> </p> <p class="text-muted text-[10px]"> </p></div> <div class="bg-surface2/40 rounded p-3"><p class="text-muted text-[10px] uppercase">Top model</p> <p class="text-fg text-sm truncate"> </p> <p class="text-muted text-[10px]"> </p></div>',1),q0=ie("<option> </option>"),Y0=ie('<p class="text-err px-4 py-2"> </p>'),K0=ie('<div class="absolute left-0 right-0"></div>'),Z0=ie('<div class="flex flex-col items-center flex-shrink-0" style="width: 16px;"><div class="relative w-full" style="height: 130px;"></div> <span class="text-[8px] text-muted mt-0.5 rotate-45 origin-top-left whitespace-nowrap" style="height: 24px;"> </span></div>'),J0=ie('<span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm"></span> </span>'),Q0=ie('<div class="flex items-end gap-1 h-40 overflow-x-auto"></div> <div class="flex flex-wrap gap-3 mt-3 text-[10px] text-muted"></div>',1),j0=ie('<p class="text-muted">No usage rows in window. Try asking Zeus something or extend the window.</p>'),eb=ie('<tr class="border-t border-border/20"><td class="py-1 text-fg"><span class="inline-block w-2 h-2 rounded-sm mr-1"></span> </td><td class="py-1 text-right text-fg"> </td><td class="py-1 text-right text-fg"> </td><td class="py-1 text-right text-muted"> </td></tr>'),tb=ie('<tr class="border-t border-border/20"><td class="py-1 text-fg truncate" style="max-width: 200px;"> </td><td class="py-1 text-right text-fg"> </td><td class="py-1 text-right text-fg"> </td></tr>'),nb=ie('<p class="text-fg text-[11px] mt-2"> </p>'),ib=ie('<p class="text-muted text-[10px] mt-2">No files dropped yet.</p>'),rb=ie(`<div class="h-full w-full flex flex-col font-mono text-xs overflow-y-auto"><div class="px-4 py-3 grid grid-cols-2 lg:grid-cols-4 gap-3 border-b border-border/40"><!></div> <div class="px-4 py-2 border-b border-border/40 flex items-center gap-3 text-[10px] text-muted"><label>Window: <select class="bg-surface text-fg ml-1 rounded p-0.5 border border-border/40"><option>1 day</option><option>7 days</option><option>30 days</option><option>90 days</option><option>1 year</option><option>all time</option></select></label> <label>Provider: <select class="bg-surface text-fg ml-1 rounded p-0.5 border border-border/40"><option>all</option><!></select></label> <button class="ml-auto text-muted hover:text-fg">refresh</button></div> <!> <section class="px-4 py-3 border-b border-border/40"><h3 class="text-accent text-sm mb-2">Daily token volume by provider</h3> <!></section> <div class="grid lg:grid-cols-2 gap-4 px-4 py-3 border-b border-border/40"><div><h4 class="text-accent text-[11px] uppercase mb-1">By provider</h4> <table class="w-full"><thead class="text-muted text-[10px] text-left"><tr><th>Provider</th><th class="text-right">Tokens</th><th class="text-right">Cost</th><th class="text-right">Calls</th></tr></thead><tbody></tbody></table></div> <div><h4 class="text-accent text-[11px] uppercase mb-1">Top callers</h4> <table class="w-full"><thead class="text-muted text-[10px] text-left"><tr><th>Caller</th><th class="text-right">Tokens</th><th class="text-right">Cost</th></tr></thead><tbody></tbody></table></div></div> <section class="px-4 py-3"><h3 class="text-accent text-sm mb-1">Historical import</h3> <p class="text-muted leading-relaxed">This view tracks usage going forward. To backfill past Claude and Cursor spend,
      drop CSV exports into <code class="text-fg"> </code> and an importer (zeus/core/usage_import.py) will fold them in. The parser is stubbed today —
      see <code>zeus/docs/token-usage.md</code> for the expected schema.</p> <!> <button class="mt-2 text-[10px] px-2 py-1 border border-accent text-accent rounded hover:bg-accent hover:text-bg">Check import dir</button></section></div>`);function Jc(n,e){Mt(e,!1);const t=ue(),i=ue();ft(e,"app",8)();let a=ue(null),o=ue(""),l=ue(30),c=ue(""),u=ue(null),f=null;const h={anthropic:"#cba6f7",anthropic_haiku:"#b4befe",gemini_paid:"#f9e2af",groq:"#f38ba8",openrouter:"#fab387",ollama:"#a6e3a1",cursor:"#94e2d5",unknown:"#6c7086"},d=_e=>h[_e]??h.unknown;async function p(){try{W(a,await $0({bucket:"day",since_days:s(l),provider:s(c)||void 0})),W(o,"")}catch(_e){W(o,String(_e))}}zt(async()=>{await p();try{const _e=await Nd();W(u,{import_dir:_e.import_dir,found_files:_e.found_files})}catch{}f=setInterval(p,3e4)}),Jt(()=>{f&&clearInterval(f)});function m(_e){return _e<1e3?_e.toString():_e<1e6?(_e/1e3).toFixed(1)+"K":(_e/1e6).toFixed(2)+"M"}function E(_e){return _e===0?"$0":_e<.01?"<$0.01":(_e<1,"$"+_e.toFixed(2))}lt(()=>s(a),()=>{W(t,(()=>{if(!s(a))return{points:[],providers:[],max:0};const _e=new Map,De=new Set;for(const Fe of s(a).series){De.add(Fe.provider);const P=Fe.tokens_in+Fe.tokens_out,x=_e.get(Fe.bucket)??new Map;x.set(Fe.provider,(x.get(Fe.provider)??0)+P),_e.set(Fe.bucket,x)}const Ne=[...De].sort(),Oe=[..._e.keys()].sort();let J=0;return{points:Oe.map(Fe=>{const P=_e.get(Fe);let x=0;const Z=[];for(const ae of Ne){const de=P.get(ae)??0;Z.push({provider:ae,tokens:de,from:x,to:x+de}),x+=de}return x>J&&(J=x),{bucket:Fe,total:x,parts:Z}}),providers:Ne,max:J}})())}),lt(()=>s(t),()=>{W(i,Math.max(280,s(t).points.length*18))}),Ht(),wt();var g=rb(),_=M(g),O=M(_);{var D=_e=>{var De=X0(),Ne=Pt(De),Oe=M(Ne),J=M(Oe);S(Oe);var We=U(Oe,2),Fe=M(We,!0);S(We);var P=U(We,2),x=M(P);S(P),S(Ne);var Z=U(Ne,2),ae=M(Z),de=M(ae);S(ae);var Le=U(ae,2),He=M(Le,!0);S(Le);var Se=U(Le,2),we=M(Se);S(Se),S(Z);var Ge=U(Z,2),Je=U(M(Ge),2),Pe=M(Je,!0);S(Je);var Ce=U(Je,2),qe=M(Ce);S(Ce),S(Ge);var je=U(Ge,2),st=U(M(je),2),ce=M(st,!0);S(st);var Be=U(st,2),Te=M(Be,!0);S(Be),S(je),me((Ve,Ye,Ue,nt,$e,It)=>{ee(J,`Tokens · ${s(a),L(()=>s(a).window.since_days)??""}d`),ee(Fe,Ve),ee(x,`${Ye??""} in · ${Ue??""} out`),ee(de,`Cost · ${s(a),L(()=>s(a).window.since_days)??""}d`),ee(He,nt),ee(we,`${s(a),L(()=>s(a).totals.calls)??""} calls`),ee(Pe,(s(a),L(()=>{var yt;return((yt=s(a).by_provider[0])==null?void 0:yt.provider)??"–"}))),ee(qe,`${$e??""} tokens`),ee(ce,(s(a),L(()=>{var yt;return((yt=s(a).by_model[0])==null?void 0:yt.model)??"–"}))),ee(Te,It)},[()=>(s(a),L(()=>m(s(a).totals.tokens))),()=>(s(a),L(()=>m(s(a).totals.tokens_in))),()=>(s(a),L(()=>m(s(a).totals.tokens_out))),()=>(s(a),L(()=>E(s(a).totals.cost_usd))),()=>(s(a),L(()=>{var Ve;return m(((Ve=s(a).by_provider[0])==null?void 0:Ve.tokens)??0)})),()=>(s(a),L(()=>{var Ve;return E(((Ve=s(a).by_model[0])==null?void 0:Ve.cost_usd)??0)}))]),j(_e,De)};Ae(O,_e=>{s(a)&&_e(D)})}S(_);var y=U(_,2),B=M(y),R=U(M(B)),C=M(R);C.value=C.__value=1;var b=U(C);b.value=b.__value=7;var A=U(b);A.value=A.__value=30;var k=U(A);k.value=k.__value=90;var z=U(k);z.value=z.__value=365;var H=U(z);H.value=H.__value=3650,S(R),S(B);var q=U(B,2),Q=U(M(q)),G=M(Q);G.value=G.__value="";var T=U(G);ct(T,1,()=>(s(a),L(()=>{var _e;return((_e=s(a))==null?void 0:_e.by_provider)??[]})),$n,(_e,De)=>{var Ne=q0(),Oe=M(Ne,!0);S(Ne);var J={};me(()=>{ee(Oe,(s(De),L(()=>s(De).provider))),J!==(J=(s(De),L(()=>s(De).provider)))&&(Ne.value=(Ne.__value=(s(De),L(()=>s(De).provider)))??"")}),j(_e,Ne)}),S(Q),S(q);var w=U(q,2);S(y);var I=U(y,2);{var F=_e=>{var De=Y0(),Ne=M(De,!0);S(De),me(()=>ee(Ne,s(o))),j(_e,De)};Ae(I,_e=>{s(o)&&_e(F)})}var Y=U(I,2),te=U(M(Y),2);{var X=_e=>{var De=Q0(),Ne=Pt(De);ct(Ne,5,()=>(s(t),L(()=>s(t).points)),J=>J.bucket,(J,We)=>{var Fe=Z0(),P=M(Fe);ct(P,5,()=>(s(We),L(()=>s(We).parts)),ae=>ae.provider,(ae,de)=>{var Le=Ai(),He=Pt(Le);{var Se=we=>{var Ge=K0();me((Je,Pe)=>{Ln(Ge,`background: ${Je??""}; bottom: ${s(de),s(t),L(()=>s(de).from/s(t).max*100)??""}%; height: ${s(de),s(t),L(()=>(s(de).to-s(de).from)/s(t).max*100)??""}%;`),$t(Ge,"title",`${s(de),L(()=>s(de).provider)??""}: ${Pe??""} on ${s(We),L(()=>s(We).bucket)??""}`)},[()=>(s(de),L(()=>d(s(de).provider))),()=>(s(de),L(()=>m(s(de).tokens)))]),j(we,Ge)};Ae(He,we=>{s(de),L(()=>s(de).tokens>0)&&we(Se)})}j(ae,Le)}),S(P);var x=U(P,2),Z=M(x,!0);S(x),S(Fe),me(ae=>ee(Z,ae),[()=>(s(We),L(()=>s(We).bucket.slice(5)))]),j(J,Fe)}),S(Ne);var Oe=U(Ne,2);ct(Oe,5,()=>(s(t),L(()=>s(t).providers)),$n,(J,We)=>{var Fe=J0(),P=M(Fe),x=U(P);S(Fe),me(Z=>{Ln(P,`background: ${Z??""};`),ee(x,` ${s(We)??""}`)},[()=>(s(We),L(()=>d(s(We))))]),j(J,Fe)}),S(Oe),me(()=>Ln(Ne,`min-width: ${s(i)??""}px;`)),j(_e,De)},K=_e=>{var De=j0();j(_e,De)};Ae(te,_e=>{s(t),L(()=>s(t).points.length>0)?_e(X):_e(K,-1)})}S(Y);var se=U(Y,2),ne=M(se),N=U(M(ne),2),V=U(M(N));ct(V,5,()=>(s(a),L(()=>{var _e;return((_e=s(a))==null?void 0:_e.by_provider)??[]})),$n,(_e,De)=>{var Ne=eb(),Oe=M(Ne),J=M(Oe),We=U(J);S(Oe);var Fe=U(Oe),P=M(Fe,!0);S(Fe);var x=U(Fe),Z=M(x,!0);S(x);var ae=U(x),de=M(ae,!0);S(ae),S(Ne),me((Le,He,Se)=>{Ln(J,`background: ${Le??""};`),ee(We,` ${s(De),L(()=>s(De).provider)??""}`),ee(P,He),ee(Z,Se),ee(de,(s(De),L(()=>s(De).calls)))},[()=>(s(De),L(()=>d(s(De).provider))),()=>(s(De),L(()=>m(s(De).tokens))),()=>(s(De),L(()=>E(s(De).cost_usd)))]),j(_e,Ne)}),S(V),S(N),S(ne);var re=U(ne,2),Me=U(M(re),2),fe=U(M(Me));ct(fe,5,()=>(s(a),L(()=>{var _e;return(((_e=s(a))==null?void 0:_e.by_caller)??[]).slice(0,10)})),$n,(_e,De)=>{var Ne=tb(),Oe=M(Ne),J=M(Oe,!0);S(Oe);var We=U(Oe),Fe=M(We,!0);S(We);var P=U(We),x=M(P,!0);S(P),S(Ne),me((Z,ae)=>{ee(J,(s(De),L(()=>s(De).caller))),ee(Fe,Z),ee(x,ae)},[()=>(s(De),L(()=>m(s(De).tokens))),()=>(s(De),L(()=>E(s(De).cost_usd)))]),j(_e,Ne)}),S(fe),S(Me),S(re),S(se);var oe=U(se,2),ve=U(M(oe),2),ye=U(M(ve)),Ie=M(ye,!0);S(ye),kn(3),S(ve);var be=U(ve,2);{var ke=_e=>{var De=nb(),Ne=M(De);S(De),me(Oe=>ee(Ne,`Pending imports: ${Oe??""}`),[()=>(s(u),L(()=>s(u).found_files.join(", ")))]),j(_e,De)},xe=_e=>{var De=ib();j(_e,De)};Ae(be,_e=>{s(u),L(()=>s(u)&&s(u).found_files.length>0)?_e(ke):_e(xe,-1)})}var Ee=U(be,2);S(oe),S(g),me(()=>ee(Ie,(s(u),L(()=>{var _e;return((_e=s(u))==null?void 0:_e.import_dir)??"~/.zeus/usage-imports/"})))),Ni(R,()=>s(l),_e=>W(l,_e)),Re("change",R,p),Ni(Q,()=>s(c),_e=>W(c,_e)),Re("change",Q,p),Re("click",w,p),Re("click",Ee,async()=>{try{const _e=await Nd();mt({title:"Importer",body:_e.note,kind:"info",ttlMs:4e3}),W(u,{import_dir:_e.import_dir,found_files:_e.found_files})}catch(_e){mt({title:"Import failed",body:String(_e).slice(0,160),kind:"err"})}}),j(n,g),Tt()}function ab(){return dt("/models")}function sb(){return dt("/models/active")}function ob(n){return dt("/models/active",{method:"POST",body:JSON.stringify({model:n})})}function lb(){return dt("/models/benchmarks")}function cb(){return dt("/integrations/telegram/status")}var ub=ie('<p class="text-err"> </p>'),db=ie("<span> </span>"),fb=ie('<p class="text-fg"><span class="text-muted"> </span> <!></p>'),hb=ie('<p class="text-muted">loading…</p>'),pb=ie('<li><button><div><p class="text-fg"> </p> <p class="text-muted text-[10px]"> </p></div> <span class="text-muted text-[10px]"> </span></button></li>'),mb=ie(`<li class="text-muted text-[11px]">No models found. If you're in dev mode (ZEUS_LLM=claude) this lists Claude options instead of Ollama.</li>`),gb=ie('<details><summary class="text-muted cursor-pointer text-[11px]">raw results</summary> <pre class="mt-2 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto"> </pre></details>'),_b=ie('<p class="text-muted text-[11px]">No benchmark data yet. Run <code class="text-fg">python -m zeus.bench</code> on the host or <code class="text-fg">POST /models/benchmarks/run</code> to populate.</p>'),vb=ie('<pre class="text-[10px] text-fg whitespace-pre-wrap"> </pre>'),xb=ie('<p class="text-muted text-[11px]">Bridge status unavailable.</p>'),bb=ie('<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-5"><!> <section><h3 class="text-accent text-sm mb-2">Active model</h3> <!> <div class="mt-3"><p class="text-muted text-[10px] uppercase mb-1"> </p> <ul class="space-y-1"></ul></div></section> <section><h3 class="text-accent text-sm mb-2">Benchmarks</h3> <!></section> <section><h3 class="text-accent text-sm mb-2">Telegram bridge</h3> <!></section> <section><h3 class="text-accent text-sm mb-2">Window manager</h3> <p class="text-muted text-[11px] leading-relaxed">Theme and modifier-key (Super / Alt / Ctrl+Alt) live in the launcher (Ctrl+Space → search "theme" / "modifier"). Persisted to <code class="text-fg">~/.zeus/zeus-os/config.json</code>.</p></section></div>');function Qc(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue(null),r=ue([]),a=ue(""),o=ue(null),l=ue(null),c=ue(!1),u=ue("");async function f(){try{const[w,I]=await Promise.all([sb(),ab()]);W(i,w),W(a,I.provider),W(r,I.models),W(u,"")}catch(w){W(u,String(w))}try{W(o,await lb())}catch{W(o,null)}try{W(l,await cb())}catch{W(l,null)}}async function h(w){if(!(!s(i)||s(i).model===w||s(c))){W(c,!0);try{W(i,await ob(w)),mt({title:"Model active",body:w,kind:"ok",ttlMs:2200})}catch(I){mt({title:"Switch failed",body:String(I).slice(0,160),kind:"err"})}finally{W(c,!1)}}}function d(w){if(!w)return"";const I=w/1024**3;return I>=1?I.toFixed(2)+" GB":(w/1024**2).toFixed(0)+" MB"}zt(f),wt();var p=bb(),m=M(p);{var E=w=>{var I=ub(),F=M(I,!0);S(I),me(()=>ee(F,s(u))),j(w,I)};Ae(m,w=>{s(u)&&w(E)})}var g=U(m,2),_=U(M(g),2);{var O=w=>{var I=fb(),F=M(I),Y=M(F,!0);S(F);var te=U(F),X=U(te);{var K=se=>{var ne=db(),N=M(ne);S(ne),me(()=>{vt(ne,1,`text-[10px] ${s(i),L(()=>s(i).gpu_available?"text-ok":"text-warn")??""} ml-2`),ee(N,`GPU ${s(i),L(()=>s(i).gpu_available?"available":"cpu only")??""}`)}),j(se,ne)};Ae(X,se=>{s(i),L(()=>s(i).gpu_available!==void 0)&&se(K)})}S(I),me(()=>{ee(Y,(s(i),L(()=>s(i).provider))),ee(te,` · ${s(i),L(()=>s(i).model)??""} `)}),j(w,I)},D=w=>{var I=hb();j(w,I)};Ae(_,w=>{s(i)?w(O):w(D,-1)})}var y=U(_,2),B=M(y),R=M(B);S(B);var C=U(B,2);ct(C,5,()=>s(r),w=>w.name,(w,I)=>{var F=pb(),Y=M(F);let te;var X=M(Y),K=M(X),se=M(K,!0);S(K);var ne=U(K,2),N=M(ne);S(ne),S(X);var V=U(X,2),re=M(V,!0);S(V),S(Y),S(F),me(Me=>{var fe;te=vt(Y,1,"w-full text-left flex items-center justify-between px-2 py-1 rounded hover:bg-surface2/60",null,te,{"bg-surface2":((fe=s(i))==null?void 0:fe.model)===s(I).name}),Y.disabled=s(c),ee(se,(s(I),L(()=>s(I).name))),ee(N,`${s(I),L(()=>s(I).parameter_size||"")??""} ${s(I),L(()=>s(I).quantization_level||"")??""} ${s(I),L(()=>s(I).family||"")??""}`),ee(re,Me)},[()=>(s(I),L(()=>d(s(I).size)))]),Re("click",Y,()=>h(s(I).name)),j(w,F)},w=>{var I=mb();j(w,I)}),S(C),S(y),S(g);var b=U(g,2),A=U(M(b),2);{var k=w=>{var I=gb(),F=U(M(I),2),Y=M(F,!0);S(F),S(I),me(te=>ee(Y,te),[()=>(s(o),L(()=>JSON.stringify(s(o),null,2).slice(0,1500)))]),j(w,I)},z=nr(()=>(s(o),L(()=>s(o)&&Object.keys(s(o)).length))),H=w=>{var I=_b();j(w,I)};Ae(A,w=>{s(z)?w(k):w(H,-1)})}S(b);var q=U(b,2),Q=U(M(q),2);{var G=w=>{var I=vb(),F=M(I,!0);S(I),me(Y=>ee(F,Y),[()=>(s(l),L(()=>JSON.stringify(s(l),null,2)))]),j(w,I)},T=w=>{var I=xb();j(w,I)};Ae(Q,w=>{s(l)?w(G):w(T,-1)})}S(q),kn(2),S(p),me(()=>ee(R,`Available (${s(a)??""})`)),j(n,p),Tt()}function Sb(n){return n.text??n.memory??""}function Ma(n){const e=n.metadata??{};return{body:Sb(n),category:e.category??null,confidence:typeof e.confidence=="number"?e.confidence:null,containsPii:!!e.contains_pii,validFrom:e.valid_from??null,validUntil:e.valid_until??null,source:n.source??e.source??null,sourceId:n.source_id??e.source_id??null}}function yb(n={}){const e=new URLSearchParams;n.source&&e.set("source",n.source),n.limit&&e.set("limit",String(n.limit)),n.offset&&e.set("offset",String(n.offset));const t=e.toString();return dt(`/memory/list${t?"?"+t:""}`)}function Eb(){return dt("/memory/sources")}function Mb(n,e=25){return dt("/memory/search",{method:"POST",body:JSON.stringify({query:n,limit:e})})}function Tb(n,e){return dt(`/memory/${encodeURIComponent(n)}`,{method:"PATCH",body:JSON.stringify(e)})}function wb(n){return dt(`/memory/${encodeURIComponent(n)}`,{method:"DELETE"})}function Ab(n){return dt("/memory/delete_batch",{method:"POST",body:JSON.stringify({ids:n})})}var Rb=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"><strong>Memory error:</strong> </div>'),Cb=ie("<option> </option>"),Ib=ie('<button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded"> </button>'),Nb=ie('<li><div class="flex items-start gap-2 px-3 py-2"><input type="checkbox" class="mt-0.5"/> <button class="flex-1 text-left"><p class="text-fg whitespace-pre-wrap leading-snug"> </p> <p class="text-muted text-[10px] mt-1"> </p></button> <button class="text-err text-[10px] opacity-50 hover:opacity-100">×</button></div></li>'),Pb=ie('<li class="px-3 py-6 text-muted text-center"> </li>'),Lb=ie('<label class="text-[10px] text-muted block mb-1">memory</label> <textarea rows="6" class="w-full bg-transparent border border-border/40 rounded p-2 text-fg outline-none"></textarea> <label class="text-[10px] text-muted block mt-2 mb-1">category</label> <input class="w-full bg-transparent border-b border-border/40 text-fg outline-none"/> <button class="mt-3 px-3 py-1 rounded bg-accent text-bg text-[11px]">Save</button>',1),vs=ie('<p class="text-muted text-[10px]"> </p>'),Db=ie('<p class="text-fg whitespace-pre-wrap leading-relaxed"> </p> <p class="text-muted text-[10px] mt-3"> </p> <!> <!> <!> <!>',1),kb=ie('<header class="flex items-center justify-between mb-2"><h3 class="text-accent text-sm"> </h3> <div class="flex gap-1"><button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded"> </button> <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded">Delete</button></div></header> <!>',1),Ub=ie('<p class="text-muted text-center mt-12">Select a memory to view + edit.</p>'),Ob=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2"><input placeholder="Semantic search…" class="flex-1 bg-transparent border-b border-border/40 text-fg outline-none"/> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"><option>all sources</option><!></select> <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">refresh</button> <!> <span class="text-[10px] text-muted"> </span></header> <div class="flex-1 flex min-h-0"><ul class="w-1/2 overflow-y-auto border-r border-border/40"></ul> <section class="w-1/2 overflow-y-auto p-3"><!></section></div></div>');function jc(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue([]),a=ue([]);function o(fe){return fe.map(oe=>typeof oe=="string"?{source:oe,count:0}:oe)}let l=ue(""),c=ue(""),u=ue(!1),f=ue(""),h=ue(""),d=ue(null),p=ue(!1),m=ue(""),E=ue(""),g=null;const _=new Set;let O=0;async function D(){try{const fe=await Eb();W(a,o(fe.sources??[]))}catch{W(a,[])}}async function y(){W(u,!0);try{if(s(c).trim()){const fe=await Mb(s(c).trim(),50);W(r,fe.entries??fe.results??[])}else{const fe=await yb({source:s(l)||void 0,limit:100});W(r,fe.entries??fe.memories??[])}W(f,""),W(h,new Date().toLocaleTimeString())}catch(fe){W(f,String(fe))}finally{W(u,!1)}}function B(fe){W(d,fe),W(p,!1);const oe=Ma(fe);W(m,oe.body),W(E,oe.category??"")}function R(fe){_.has(fe)?_.delete(fe):_.add(fe),O+=1}async function C(){if(s(d))try{const fe=await Tb(s(d).id,{text:s(m),memory:s(m),metadata:{...s(d).metadata??{},category:s(E)||null}});W(d,fe),W(p,!1),mt({title:"Memory saved",kind:"ok",ttlMs:1500}),await y()}catch(fe){mt({title:"Save failed",body:String(fe).slice(0,160),kind:"err"})}}async function b(fe){var oe;if(confirm("Delete this memory?"))try{await wb(fe),((oe=s(d))==null?void 0:oe.id)===fe&&W(d,null),await y()}catch(ve){mt({title:"Delete failed",body:String(ve).slice(0,160),kind:"err"})}}async function A(){if(_.size!==0&&confirm(`Delete ${_.size} memories?`))try{const fe=await Ab([..._]);mt({title:`Deleted ${fe.deleted}`,kind:"ok",ttlMs:1800}),_.clear(),O+=1,await y()}catch(fe){mt({title:"Bulk delete failed",body:String(fe).slice(0,160),kind:"err"})}}function k(fe){if(!fe)return"";try{return new Date(fe).toLocaleString([],{dateStyle:"short",timeStyle:"short"})}catch{return fe}}zt(()=>{y(),D(),g=setInterval(y,15e3)}),Jt(()=>{g&&clearInterval(g)}),lt(()=>{},()=>{W(t,_.size)}),Ht(),wt();var z=Ob(),H=M(z);{var q=fe=>{var oe=Rb(),ve=U(M(oe));S(oe),me(()=>ee(ve,` ${s(f)??""}`)),j(fe,oe)};Ae(H,fe=>{s(f)&&fe(q)})}var Q=U(H,2),G=M(Q);gn(G);var T=U(G,2),w=M(T);w.value=w.__value="";var I=U(w);ct(I,1,()=>s(a),fe=>fe.source,(fe,oe)=>{var ve=Cb(),ye=M(ve);S(ve);var Ie={};me(()=>{ee(ye,`${s(oe),L(()=>s(oe).source)??""}${s(oe),L(()=>s(oe).count?` (${s(oe).count})`:"")??""}`),Ie!==(Ie=(s(oe),L(()=>s(oe).source)))&&(ve.value=(ve.__value=(s(oe),L(()=>s(oe).source)))??"")}),j(fe,ve)}),S(T);var F=U(T,2),Y=U(F,2);{var te=fe=>{var oe=Ib(),ve=M(oe);S(oe),me(()=>ee(ve,`delete ${s(t)??""}`)),Re("click",oe,A),j(fe,oe)};Ae(Y,fe=>{s(t)>0&&fe(te)})}var X=U(Y,2),K=M(X);S(X),S(Q);var se=U(Q,2),ne=M(se);ct(ne,5,()=>s(r),fe=>fe.id,(fe,oe)=>{const ve=tr(()=>(tt(Ma),s(oe),L(()=>Ma(s(oe)))));var ye=Nb();let Ie;var be=M(ye),ke=M(be);gn(ke);var xe=U(ke,2),Ee=M(xe),_e=M(Ee);S(Ee);var De=U(Ee,2),Ne=M(De);S(De),S(xe);var Oe=U(xe,2);S(be),S(ye),me((J,We,Fe)=>{var P;Ie=vt(ye,1,"border-b border-border/20",null,Ie,{"bg-surface2":((P=s(d))==null?void 0:P.id)===s(oe).id}),sg(ke,J),ee(_e,`${We??""}${tt(s(ve)),L(()=>s(ve).body.length>240?"…":"")??""}`),ee(Ne,`${tt(s(ve)),L(()=>s(ve).source??"(no source)")??""}${tt(s(ve)),L(()=>s(ve).category?` · ${s(ve).category}`:"")??""}
                ${Fe??""}`)},[()=>(s(oe),L(()=>_.has(s(oe).id))),()=>(tt(s(ve)),L(()=>s(ve).body.slice(0,240))),()=>(tt(s(ve)),L(()=>s(ve).confidence!==null?` · ${(s(ve).confidence*100).toFixed(0)}%`:""))]),Re("change",ke,()=>R(s(oe).id)),Re("click",xe,()=>B(s(oe))),Re("click",Oe,()=>b(s(oe).id)),j(fe,ye)},fe=>{var oe=Pb(),ve=M(oe,!0);S(oe),me(()=>ee(ve,s(u)?"loading…":"no memories matched.")),j(fe,oe)}),S(ne);var N=U(ne,2),V=M(N);{var re=fe=>{const oe=tr(()=>(tt(Ma),s(d),L(()=>Ma(s(d)))));var ve=kb(),ye=Pt(ve),Ie=M(ye),be=M(Ie);S(Ie);var ke=U(Ie,2),xe=M(ke),Ee=M(xe,!0);S(xe);var _e=U(xe,2);S(ke),S(ye);var De=U(ye,2);{var Ne=J=>{var We=Lb(),Fe=U(Pt(We),2);fo(Fe);var P=U(Fe,4);gn(P);var x=U(P,2);nn(Fe,()=>s(m),Z=>W(m,Z)),nn(P,()=>s(E),Z=>W(E,Z)),Re("click",x,C),j(J,We)},Oe=J=>{var We=Db(),Fe=Pt(We),P=M(Fe,!0);S(Fe);var x=U(Fe,2),Z=M(x);S(x);var ae=U(x,2);{var de=Pe=>{var Ce=vs(),qe=M(Ce);S(Ce),me(()=>ee(qe,`category ${tt(s(oe)),L(()=>s(oe).category)??""}`)),j(Pe,Ce)};Ae(ae,Pe=>{tt(s(oe)),L(()=>s(oe).category)&&Pe(de)})}var Le=U(ae,2);{var He=Pe=>{var Ce=vs(),qe=M(Ce);S(Ce),me(je=>ee(qe,`confidence ${je??""}%${tt(s(oe)),L(()=>s(oe).containsPii?" · PII":"")??""}`),[()=>(tt(s(oe)),L(()=>(s(oe).confidence*100).toFixed(1)))]),j(Pe,Ce)};Ae(Le,Pe=>{tt(s(oe)),L(()=>s(oe).confidence!==null)&&Pe(He)})}var Se=U(Le,2);{var we=Pe=>{var Ce=vs(),qe=M(Ce);S(Ce),me(()=>ee(qe,`source ${tt(s(oe)),L(()=>s(oe).source)??""}${tt(s(oe)),L(()=>s(oe).sourceId?` (${s(oe).sourceId})`:"")??""}`)),j(Pe,Ce)};Ae(Se,Pe=>{tt(s(oe)),L(()=>s(oe).source)&&Pe(we)})}var Ge=U(Se,2);{var Je=Pe=>{var Ce=vs(),qe=M(Ce);S(Ce),me((je,st)=>ee(qe,`valid ${je??""} — ${st??""}`),[()=>(tt(s(oe)),L(()=>k(s(oe).validFrom))),()=>(tt(s(oe)),L(()=>k(s(oe).validUntil)||"open"))]),j(Pe,Ce)};Ae(Ge,Pe=>{tt(s(oe)),L(()=>s(oe).validFrom||s(oe).validUntil)&&Pe(Je)})}me(()=>{ee(P,(tt(s(oe)),L(()=>s(oe).body))),ee(Z,`id ${s(d),L(()=>s(d).id)??""}`)}),j(J,We)};Ae(De,J=>{s(p)?J(Ne):J(Oe,-1)})}me(()=>{ee(be,`Memory · ${tt(s(oe)),L(()=>s(oe).source??"unknown")??""}`),ee(Ee,s(p)?"Cancel":"Edit")}),Re("click",xe,()=>W(p,!s(p))),Re("click",_e,()=>b(s(d).id)),j(fe,ve)},Me=fe=>{var oe=Ub();j(fe,oe)};Ae(V,fe=>{s(d)?fe(re):fe(Me,-1)})}S(N),S(se),S(z),me(()=>ee(K,`${s(r),L(()=>s(r).length)??""} ${s(u)?"loading…":""} ${s(h)??""}`)),nn(G,()=>s(c),fe=>W(c,fe)),Re("keydown",G,fe=>fe.key==="Enter"&&y()),Ni(T,()=>s(l),fe=>W(l,fe)),Re("change",T,y),Re("click",F,y),j(n,z),Tt()}function Fb(n={}){const e=new URLSearchParams;n.source&&e.set("source",n.source),n.doc_type&&e.set("doc_type",n.doc_type),n.limit&&e.set("limit",String(n.limit)),n.offset&&e.set("offset",String(n.offset));const t=e.toString();return dt(`/knowledge/list${t?"?"+t:""}`)}function Bb(){return dt("/knowledge/facets")}function zb(n,e=25){return dt("/knowledge/search",{method:"POST",body:JSON.stringify({query:n,limit:e})})}var Hb=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"><strong>Knowledge error:</strong> </div>'),Pd=ie("<option> </option>"),Gb=ie('<li><button class="w-full text-left px-3 py-2 hover:bg-surface2/60"><p class="text-fg leading-snug truncate"> </p> <p class="text-muted text-[10px] mt-1"> </p></button></li>'),Vb=ie('<li class="px-3 py-6 text-muted text-center"> </li>'),Wb=ie('<a target="_blank" rel="noopener" class="text-accent text-[10px] underline"> </a>'),$b=ie('<p class="text-muted text-[10px] mt-3"> </p>'),Xb=ie('<header class="mb-2"><h3 class="text-accent text-sm"> </h3> <p class="text-muted text-[10px] mt-1"> </p> <!></header> <pre class="text-fg whitespace-pre-wrap leading-relaxed"> </pre> <!> <p class="text-muted text-[10px] mt-2"> </p>',1),qb=ie('<p class="text-muted text-center mt-12">Select a knowledge entry to inspect.</p>'),Yb=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2 flex-wrap"><input placeholder="Hybrid search (Enter)…" class="flex-1 min-w-[140px] bg-transparent border-b border-border/40 text-fg outline-none"/> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"><option>all sources</option><!></select> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"><option>all types</option><!></select> <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">refresh</button> <span class="text-[10px] text-muted"> </span></header> <div class="flex-1 flex min-h-0"><ul class="w-1/2 overflow-y-auto border-r border-border/40"></ul> <section class="w-1/2 overflow-y-auto p-3"><!></section></div></div>');function eu(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue([]),r=ue({}),a=ue(0),o=ue(""),l=ue(""),c=ue(""),u=ue(!1),f=ue(""),h=ue(""),d=ue(null),p=null;async function m(){try{const te=await Bb(),X={};let K=0;for(const[se,ne]of Object.entries(te))se==="total"&&typeof ne=="number"?K=ne:Array.isArray(ne)&&(X[se]=ne);W(r,X),W(a,K)}catch{W(r,{})}}async function E(){W(u,!0);try{if(s(o).trim()){const te=await zb(s(o).trim(),50);W(i,te.entries??te.results??[])}else{const te=await Fb({source:s(l)||void 0,doc_type:s(c)||void 0,limit:100});W(i,te.entries??te.items??[])}W(f,""),W(h,new Date().toLocaleTimeString())}catch(te){W(f,String(te))}finally{W(u,!1)}}function g(te){if(!te)return"";try{return new Date(te).toLocaleString([],{dateStyle:"short",timeStyle:"short"})}catch{return te}}zt(()=>{E(),m(),p=setInterval(()=>{E(),m()},3e4)}),Jt(()=>{p&&clearInterval(p)}),wt();var _=Yb(),O=M(_);{var D=te=>{var X=Hb(),K=U(M(X));S(X),me(()=>ee(K,` ${s(f)??""}`)),j(te,X)};Ae(O,te=>{s(f)&&te(D)})}var y=U(O,2),B=M(y);gn(B);var R=U(B,2),C=M(R);C.value=C.__value="";var b=U(C);ct(b,1,()=>(s(r),L(()=>s(r).source??[])),te=>te.value,(te,X)=>{var K=Pd(),se=M(K);S(K);var ne={};me(()=>{ee(se,`${s(X),L(()=>s(X).value)??""} (${s(X),L(()=>s(X).count)??""})`),ne!==(ne=(s(X),L(()=>s(X).value)))&&(K.value=(K.__value=(s(X),L(()=>s(X).value)))??"")}),j(te,K)}),S(R);var A=U(R,2),k=M(A);k.value=k.__value="";var z=U(k);ct(z,1,()=>(s(r),L(()=>s(r).doc_type??[])),te=>te.value,(te,X)=>{var K=Pd(),se=M(K);S(K);var ne={};me(()=>{ee(se,`${s(X),L(()=>s(X).value)??""} (${s(X),L(()=>s(X).count)??""})`),ne!==(ne=(s(X),L(()=>s(X).value)))&&(K.value=(K.__value=(s(X),L(()=>s(X).value)))??"")}),j(te,K)}),S(A);var H=U(A,2),q=U(H,2),Q=M(q);S(q),S(y);var G=U(y,2),T=M(G);ct(T,5,()=>s(i),te=>te.id,(te,X)=>{var K=Gb();let se;var ne=M(K),N=M(ne),V=M(N,!0);S(N);var re=U(N,2),Me=M(re);S(re),S(ne),S(K),me((fe,oe)=>{var ve;se=vt(K,1,"border-b border-border/20",null,se,{"bg-surface2":((ve=s(d))==null?void 0:ve.id)===s(X).id}),ee(V,fe),ee(Me,`${s(X),L(()=>s(X).source)??""}${s(X),L(()=>s(X).doc_type?` · ${s(X).doc_type}`:"")??""}${oe??""}`)},[()=>(s(X),L(()=>s(X).title||s(X).text.slice(0,80))),()=>(s(X),L(()=>s(X).created_at?` · ${g(s(X).created_at)}`:""))]),Re("click",ne,()=>W(d,s(X))),j(te,K)},te=>{var X=Vb(),K=M(X,!0);S(X),me(()=>ee(K,s(u)?"loading…":"no knowledge matched.")),j(te,X)}),S(T);var w=U(T,2),I=M(w);{var F=te=>{var X=Xb(),K=Pt(X),se=M(K),ne=M(se,!0);S(se);var N=U(se,2),V=M(N);S(N);var re=U(N,2);{var Me=ke=>{var xe=Wb(),Ee=M(xe,!0);S(xe),me(()=>{$t(xe,"href",(s(d),L(()=>s(d).url))),ee(Ee,(s(d),L(()=>s(d).url)))}),j(ke,xe)};Ae(re,ke=>{s(d),L(()=>s(d).url)&&ke(Me)})}S(K);var fe=U(K,2),oe=M(fe,!0);S(fe);var ve=U(fe,2);{var ye=ke=>{var xe=$b(),Ee=M(xe);S(xe),me(_e=>ee(Ee,`tags: ${_e??""}`),[()=>(s(d),L(()=>s(d).tags.join(", ")))]),j(ke,xe)};Ae(ve,ke=>{s(d),L(()=>s(d).tags&&s(d).tags.length)&&ke(ye)})}var Ie=U(ve,2),be=M(Ie);S(Ie),me(()=>{ee(ne,(s(d),L(()=>s(d).title||"(untitled)"))),ee(V,`${s(d),L(()=>s(d).source)??""}${s(d),L(()=>s(d).doc_type?` · ${s(d).doc_type}`:"")??""}`),ee(oe,(s(d),L(()=>s(d).text))),ee(be,`id ${s(d),L(()=>s(d).id)??""}`)}),j(te,X)},Y=te=>{var X=qb();j(te,X)};Ae(I,te=>{s(d)?te(F):te(Y,-1)})}S(w),S(G),S(_),me(()=>ee(Q,`${s(i),L(()=>s(i).length)??""} / ${s(a)??""} total ${s(u)?"loading…":""} ${s(h)??""}`)),nn(B,()=>s(o),te=>W(o,te)),Re("keydown",B,te=>te.key==="Enter"&&E()),Ni(R,()=>s(l),te=>W(l,te)),Re("change",R,E),Ni(A,()=>s(c),te=>W(c,te)),Re("change",A,E),Re("click",H,E),j(n,_),Tt()}async function Kb(){const n=await dt("/orchestration/status"),e=[],t=n.agents??{};if(Array.isArray(t))for(const i of t)e.push(i);else for(const[i,r]of Object.entries(t))e.push({name:i,...r});return{agents:e,environment:n.environment,ruflo_version:n.ruflo_version,active_model:n.active_model,metrics:n.metrics}}function Zb(){return dt("/orchestration/tasks")}var Jb=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"><strong>Agents error:</strong> </div>'),Qb=ie('<p class="text-muted text-[10px] truncate"> </p>'),jb=ie('<li><button class="w-full text-left px-3 py-2 hover:bg-surface2/60"><div class="flex items-center justify-between"><span class="text-fg"> </span> <span> </span></div> <!> <p class="text-muted text-[10px] mt-0.5"> </p></button></li>'),eS=ie('<li class="px-3 py-6 text-muted text-center">No agents loaded.</li>'),tS=ie('<p class="text-fg/80 mb-2"> </p>'),nS=ie("<li> </li>"),iS=ie('<p class="text-[10px] text-muted">tools</p> <ul class="text-fg/80 text-[11px] mb-2"></ul>',1),rS=ie('<p class="text-[10px] text-muted">models</p> <p class="text-fg/80 text-[11px] mb-2"> </p>',1),aS=ie('<p class="text-[10px] text-muted">safety policy</p> <p class="text-fg/80 text-[11px] mb-2"> </p>',1),sS=ie('<p class="text-err text-[11px] mb-2"> </p>'),oS=ie('<header class="mb-2"><h3 class="text-accent text-sm"> </h3> <p class="text-muted text-[10px]"> </p></header> <!> <!> <!> <!> <!>',1),lS=ie('<p class="text-muted text-center mb-4">Select an agent to inspect its definition.</p>'),cS=ie('<p class="text-err text-[10px]"> </p>'),uS=ie('<li class="border-b border-border/20 py-1"><div class="flex items-center justify-between text-[10px] text-muted"><span> </span> <span> </span></div> <!></li>'),dS=ie('<li class="text-muted text-[10px]">No tasks in the bus.</li>'),fS=ie('<details class="mt-4"><summary class="text-muted text-[10px] cursor-pointer">bus metrics</summary> <pre class="mt-1 text-[10px] text-fg/80 whitespace-pre-wrap"> </pre></details>'),hS=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="px-3 py-2 border-b border-border/40 flex items-center justify-between"><div><h3 class="text-accent text-sm">Agents</h3> <p class="text-muted text-[10px]"> </p></div> <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">refresh</button></header> <div class="flex-1 flex min-h-0"><ul class="w-1/2 overflow-y-auto border-r border-border/40"></ul> <section class="w-1/2 overflow-y-auto p-3"><!> <header class="mt-4 mb-1"><h3 class="text-accent text-sm">Recent tasks</h3></header> <ul class="space-y-1"></ul> <!></section></div></div>');function tu(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue([]),r=ue([]),a=ue(),o=ue(""),l=ue(""),c=ue(!1),u=null,f=ue(null);async function h(){W(c,!0);try{const[G,T]=await Promise.all([Kb(),Zb()]);W(i,G.agents??[]),W(a,G.metrics),W(r,Array.isArray(T)?T:T.tasks??[]),W(o,""),W(l,new Date().toLocaleTimeString())}catch(G){W(o,String(G))}finally{W(c,!1)}}function d(G){return!G||G<=0?"":G<60?`${Math.round(G)}s`:G<3600?`${(G/60).toFixed(1)}m`:G<86400?`${(G/3600).toFixed(1)}h`:`${(G/86400).toFixed(1)}d`}function p(G){return G?Array.isArray(G)?G.join(", "):Object.entries(G).map(([T,w])=>`${T}=${w}`).join(" · "):""}zt(()=>{h(),u=setInterval(h,8e3)}),Jt(()=>{u&&clearInterval(u)}),wt();var m=hS(),E=M(m);{var g=G=>{var T=Jb(),w=U(M(T));S(T),me(()=>ee(w,` ${s(o)??""}`)),j(G,T)};Ae(E,G=>{s(o)&&G(g)})}var _=U(E,2),O=M(_),D=U(M(O),2),y=M(D);S(D),S(O);var B=U(O,2);S(_);var R=U(_,2),C=M(R);ct(C,5,()=>s(i),G=>G.name,(G,T)=>{var w=jb();let I;var F=M(w),Y=M(F),te=M(Y),X=M(te,!0);S(te);var K=U(te,2),se=M(K,!0);S(K),S(Y);var ne=U(Y,2);{var N=Me=>{var fe=Qb(),oe=M(fe,!0);S(fe),me(()=>ee(oe,(s(T),L(()=>s(T).description)))),j(Me,fe)};Ae(ne,Me=>{s(T),L(()=>s(T).description)&&Me(N)})}var V=U(ne,2),re=M(V);S(V),S(F),S(w),me((Me,fe)=>{var oe;I=vt(w,1,"border-b border-border/20",null,I,{"bg-surface2":((oe=s(f))==null?void 0:oe.name)===s(T).name}),ee(X,(s(T),L(()=>s(T).name))),vt(K,1,`text-[10px] ${s(T),L(()=>s(T).status==="running"||s(T).status==="idle"?"text-ok":"text-muted")??""}`),ee(se,(s(T),L(()=>s(T).status??"?"))),ee(re,`${Me??""}${fe??""}`)},[()=>(s(T),L(()=>s(T).model??p(s(T).models))),()=>(s(T),L(()=>s(T).uptime_seconds?` · up ${d(s(T).uptime_seconds)}`:""))]),Re("click",F,()=>W(f,s(T))),j(G,w)},G=>{var T=eS();j(G,T)}),S(C);var b=U(C,2),A=M(b);{var k=G=>{var T=oS(),w=Pt(T),I=M(w),F=M(I,!0);S(I);var Y=U(I,2),te=M(Y,!0);S(Y),S(w);var X=U(w,2);{var K=ve=>{var ye=tS(),Ie=M(ye,!0);S(ye),me(()=>ee(Ie,(s(f),L(()=>s(f).description)))),j(ve,ye)};Ae(X,ve=>{s(f),L(()=>s(f).description)&&ve(K)})}var se=U(X,2);{var ne=ve=>{var ye=iS(),Ie=U(Pt(ye),2);ct(Ie,5,()=>(s(f),L(()=>s(f).tools)),$n,(be,ke)=>{var xe=nS(),Ee=M(xe);S(xe),me(()=>ee(Ee,`· ${s(ke)??""}`)),j(be,xe)}),S(Ie),j(ve,ye)};Ae(se,ve=>{s(f),L(()=>s(f).tools&&s(f).tools.length)&&ve(ne)})}var N=U(se,2);{var V=ve=>{var ye=rS(),Ie=U(Pt(ye),2),be=M(Ie,!0);S(Ie),me(ke=>ee(be,ke),[()=>(s(f),L(()=>s(f).model||p(s(f).models)))]),j(ve,ye)};Ae(N,ve=>{s(f),L(()=>s(f).model||s(f).models)&&ve(V)})}var re=U(N,2);{var Me=ve=>{var ye=aS(),Ie=U(Pt(ye),2),be=M(Ie,!0);S(Ie),me(()=>ee(be,(s(f),L(()=>s(f).safety_policy)))),j(ve,ye)};Ae(re,ve=>{s(f),L(()=>s(f).safety_policy)&&ve(Me)})}var fe=U(re,2);{var oe=ve=>{var ye=sS(),Ie=M(ye);S(ye),me(()=>ee(Ie,`error: ${s(f),L(()=>s(f).error)??""}`)),j(ve,ye)};Ae(fe,ve=>{s(f),L(()=>s(f).error)&&ve(oe)})}me(()=>{ee(F,(s(f),L(()=>s(f).name))),ee(te,(s(f),L(()=>s(f).status??"unknown")))}),j(G,T)},z=G=>{var T=lS();j(G,T)};Ae(A,G=>{s(f)?G(k):G(z,-1)})}var H=U(A,4);ct(H,5,()=>(s(r),L(()=>s(r).slice(0,15))),G=>G.task_id,(G,T)=>{var w=uS(),I=M(w),F=M(I),Y=M(F);S(F);var te=U(F,2);let X;var K=M(te,!0);S(te),S(I);var se=U(I,2);{var ne=N=>{var V=cS(),re=M(V,!0);S(V),me(()=>ee(re,(s(T),L(()=>s(T).error)))),j(N,V)};Ae(se,N=>{s(T),L(()=>s(T).error)&&N(ne)})}S(w),me(()=>{ee(Y,`${s(T),L(()=>s(T).agent)??""} · ${s(T),L(()=>s(T).action)??""}`),X=vt(te,1,"text-fg",null,X,{"text-ok":s(T).status==="done","text-err":s(T).status==="error"}),ee(K,(s(T),L(()=>s(T).status)))}),j(G,w)},G=>{var T=dS();j(G,T)}),S(H);var q=U(H,2);{var Q=G=>{var T=fS(),w=U(M(T),2),I=M(w,!0);S(w),S(T),me(F=>ee(I,F),[()=>(s(a),L(()=>JSON.stringify(s(a),null,2)))]),j(G,T)};Ae(q,G=>{s(a)&&G(Q)})}S(b),S(R),S(m),me(()=>ee(y,`${s(i),L(()=>s(i).length)??""} loaded · ${s(r),L(()=>s(r).length)??""} tasks · ${s(c)?"loading…":""} ${s(l)??""}`)),Re("click",B,h),j(n,m),Tt()}function pS(){return dt("/admin/ingest/stats")}function mS(n){return dt("/ingest/trigger",{method:"POST",body:JSON.stringify(n)})}var gS=ie('<div class="bg-err/20 border border-err/40 rounded px-3 py-2 text-err"><strong>Ingest error:</strong> </div>'),_S=ie('<p class="text-warn text-[11px]"> </p>'),vS=ie('<tr class="border-t border-border/20"><td class="py-1 text-fg"> </td><td class="py-1 text-right text-fg"> </td><td class="py-1 text-right text-muted"> </td><td class="py-1 text-right text-muted"> </td><td class="py-1 text-right text-muted"> </td></tr>'),xS=ie('<table class="w-full"><thead class="text-muted text-[10px] text-left"><tr><th>Collection</th><th class="text-right">Points</th><th class="text-right">Vectors</th><th class="text-right">Indexed</th><th class="text-right">Status</th></tr></thead><tbody></tbody></table>'),bS=ie('<p class="text-muted">No collection stats.</p>'),SS=ie('<p class="text-muted text-[10px] mt-2"> </p>'),yS=ie('<button class="flex items-center justify-between px-3 py-2 rounded border border-border/40 hover:border-accent text-left"><div><p class="text-fg"> </p> <p class="text-muted text-[10px]"> </p></div> <span class="text-accent text-[11px]">▶</span></button>'),ES=ie(`<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-4"><!> <header><h3 class="text-accent text-sm">Iris · ingest</h3> <p class="text-muted text-[10px]"> </p></header> <section><h4 class="text-accent text-[11px] uppercase mb-1">Collections</h4> <!> <!></section> <section><h4 class="text-accent text-[11px] uppercase mb-1">Trigger</h4> <div class="grid grid-cols-2 gap-2"></div> <p class="text-muted text-[10px] mt-3 leading-relaxed">Triggers <code class="text-fg">POST /ingest/trigger</code>; routing follows
      zeus/ingest/config.yaml. Profile sources fan out into the memory store via
      LLM fact extraction; knowledge sources go raw into <code class="text-fg">zeus_knowledge</code>.</p></section></div>`);function nu(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue(null),r=ue(""),a=ue(""),o=ue(!1),l=null;const c=[{id:"context_pack",label:"Context pack",kind:"profile"},{id:"gcal",label:"Google Calendar",kind:"profile"},{id:"obsidian",label:"Obsidian vault",kind:"knowledge"},{id:"chatgpt",label:"ChatGPT export",kind:"knowledge"},{id:"newsletter",label:"Newsletters",kind:"knowledge"},{id:"bookmarks",label:"Bookmarks",kind:"knowledge"},{id:"email",label:"Email (IMAP)",kind:"knowledge"},{id:"git",label:"Git commits",kind:"knowledge"},{id:"kiwix",label:"Kiwix ZIM",kind:"reference"}];async function u(){try{W(i,await pS()),W(r,""),W(a,new Date().toLocaleTimeString())}catch(H){W(r,String(H))}}async function f(H){W(o,!0);try{const q=await mS({source:H});mt({title:`Ingest queued: ${H}`,body:q.status,kind:"ok",ttlMs:2200}),await u()}catch(q){mt({title:"Trigger failed",body:String(q).slice(0,160),kind:"err"})}finally{W(o,!1)}}function h(H){return H<1e3?String(H):H<1e6?(H/1e3).toFixed(1)+"K":(H/1e6).toFixed(2)+"M"}zt(()=>{u(),l=setInterval(u,2e4)}),Jt(()=>{l&&clearInterval(l)}),wt();var d=ES(),p=M(d);{var m=H=>{var q=gS(),Q=U(M(q));S(q),me(()=>ee(Q,` ${s(r)??""}`)),j(H,q)};Ae(p,H=>{s(r)&&H(m)})}var E=U(p,2),g=U(M(E),2),_=M(g,!0);S(g),S(E);var O=U(E,2),D=U(M(O),2);{var y=H=>{var q=_S(),Q=M(q);S(q),me(()=>ee(Q,`backend: ${s(i),L(()=>s(i).error)??""}`)),j(H,q)},B=H=>{var q=xS(),Q=U(M(q));ct(Q,5,()=>(s(i),L(()=>Object.entries(s(i).collections))),([G,T])=>G,(G,T)=>{var w=nr(()=>jf(s(T),2));let I=()=>s(w)[0],F=()=>s(w)[1];var Y=vS(),te=M(Y),X=M(te,!0);S(te);var K=U(te),se=M(K,!0);S(K);var ne=U(K),N=M(ne,!0);S(ne);var V=U(ne),re=M(V,!0);S(V);var Me=U(V),fe=M(Me,!0);S(Me),S(Y),me((oe,ve,ye)=>{ee(X,I()),ee(se,oe),ee(N,ve),ee(re,ye),ee(fe,(F(),L(()=>F().status??"")))},[()=>(F(),L(()=>F().points_count!==null&&F().points_count!==void 0?h(F().points_count):"–")),()=>(F(),L(()=>F().vectors_count!==null&&F().vectors_count!==void 0?h(F().vectors_count):"–")),()=>(F(),L(()=>F().indexed_vectors_count!==null&&F().indexed_vectors_count!==void 0?h(F().indexed_vectors_count):"–"))]),j(G,Y)}),S(Q),S(q),j(H,q)},R=nr(()=>(s(i),L(()=>{var H;return((H=s(i))==null?void 0:H.collections)&&Object.keys(s(i).collections).length}))),C=H=>{var q=bS();j(H,q)};Ae(D,H=>{s(i),L(()=>{var q;return(q=s(i))==null?void 0:q.error})?H(y):s(R)?H(B,1):H(C,-1)})}var b=U(D,2);{var A=H=>{var q=SS(),Q=M(q);S(q),me(()=>ee(Q,`last ingest: ${s(i),L(()=>s(i).last_ingest_at)??""}`)),j(H,q)};Ae(b,H=>{s(i),L(()=>{var q;return(q=s(i))==null?void 0:q.last_ingest_at})&&H(A)})}S(O);var k=U(O,2),z=U(M(k),2);ct(z,5,()=>c,H=>H.id,(H,q)=>{var Q=yS(),G=M(Q),T=M(G),w=M(T,!0);S(T);var I=U(T,2),F=M(I);S(I),S(G),kn(2),S(Q),me(()=>{Q.disabled=s(o),ee(w,(s(q),L(()=>s(q).label))),ee(F,`→ ${s(q),L(()=>s(q).kind)??""}`)}),Re("click",Q,()=>f(s(q).id)),j(H,Q)}),S(z),kn(2),S(k),S(d),me(()=>ee(_,s(a)?`last refresh ${s(a)}`:"loading…")),j(n,d),Tt()}function MS(){return dt("/zeus-os/vault/tree")}function TS(){return dt("/zeus-os/vault/index")}function wS(n){return dt(`/zeus-os/vault/file?path=${encodeURIComponent(n)}`)}function AS(n,e,t){if(!e)return null;const i=n.replace(/\.(md|markdown)$/i,"");if(e.paths.includes(i+".md"))return i+".md";if(e.paths.includes(i))return i;const r=e.by_title[i]??[];if(r.length===0)return null;if(r.length===1)return r[0];if(t){const a=t.split("/").slice(0,-1).join("/"),o=r.find(l=>l.startsWith(a+"/"));if(o)return o}return r[0]}var RS=ie('<div><button class="w-full text-left px-2 py-0.5 hover:bg-surface2/60 text-fg flex items-center"><span class="inline-block w-3 text-muted"> </span> <span class="ml-1 truncate"> </span></button> <!></div>'),CS=ie('<button><span class="inline-block w-3 text-muted text-[10px]"> </span> <span class="ml-1 truncate"> </span></button>');function dp(n,e){Mt(e,!1);const t=ue();let i=ft(e,"node",8),r=ft(e,"openFolders",8),a=ft(e,"currentPath",8),o=ft(e,"toggle",8),l=ft(e,"pick",8),c=ft(e,"depth",8,0);lt(()=>tt(c()),()=>{W(t,c()*12)}),Ht(),wt();var u=Ai(),f=Pt(u);{var h=p=>{var m=RS(),E=M(m);let g;var _=M(E),O=M(_,!0);S(_);var D=U(_,2),y=M(D,!0);S(D),S(E);var B=U(E,2);{var R=C=>{var b=Ai(),A=Pt(b);ct(A,1,()=>(tt(i()),L(()=>i().children??[])),k=>k.path,(k,z)=>{var H=Ai(),q=Pt(H);{let Q=tr(()=>c()+1);dp(q,{get node(){return s(z)},get openFolders(){return r()},get currentPath(){return a()},get toggle(){return o()},get pick(){return l()},get depth(){return s(Q)}})}j(k,H)}),j(C,b)};Ae(B,C=>{tt(r()),tt(i()),L(()=>r()[i().path])&&C(R)})}S(m),me(()=>{g=Ln(E,"",g,{"padding-left":`${s(t)+8}px`}),ee(O,(tt(r()),tt(i()),L(()=>r()[i().path]?"▾":"▸"))),ee(y,(tt(i()),L(()=>i().name)))}),Re("click",E,()=>o()(i().path)),j(p,m)},d=p=>{var m=CS();let E,g;var _=M(m),O=M(_,!0);S(_);var D=U(_,2),y=M(D,!0);S(D),S(m),me(()=>{E=vt(m,1,"w-full text-left px-2 py-0.5 hover:bg-surface2/60 truncate flex items-center",null,E,{"text-accent":a()===i().path,"text-fg":a()!==i().path}),g=Ln(m,"",g,{"padding-left":`${s(t)+8}px`}),ee(O,(tt(i()),L(()=>i().kind==="doc"?"·":i().kind==="image"?"🖼":"·"))),ee(y,(tt(i()),L(()=>i().name)))}),Re("click",m,()=>i().kind==="doc"&&l()(i().path)),j(p,m)};Ae(f,p=>{tt(i()),L(()=>i().kind==="dir")?p(h):p(d,-1)})}j(n,u),Tt()}var IS=ie('<p class="text-err px-3 py-2 text-[11px]"> </p>'),NS=ie('<p class="text-muted text-center mt-6 text-[11px]">loading…</p>'),PS=ie('<button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">← back</button>'),LS=ie('<pre class="text-fg/90 whitespace-pre-wrap text-[11px] leading-relaxed"> </pre>'),DS=ie('<div class="prose-chat obsidian-body" role="presentation"></div>'),kS=ie('<header class="px-3 py-1.5 border-b border-border/40 flex items-center justify-between"><div class="min-w-0"><h3 class="text-accent text-sm truncate"> </h3> <p class="text-muted text-[10px] truncate"> </p></div> <div class="flex gap-1"><!> <button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded hover:bg-accent hover:text-bg" title="Open in Editor">Edit</button> <button> </button></div></header> <div class="flex-1 overflow-y-auto p-4"><!></div>',1),US=ie('<div class="flex-1 grid place-items-center text-muted text-center px-6"><div><p>Select a markdown file from the tree.</p> <p class="mt-1 text-[10px]">Wikilinks <code class="text-fg">[[Note]]</code> and embeds <code class="text-fg">![[image.png]]</code> resolve against the vault index.</p></div></div>'),OS=ie('<div class="h-full w-full flex font-mono text-xs"><aside class="w-72 border-r border-border/40 flex flex-col"><header class="px-3 py-2 border-b border-border/40"><h3 class="text-accent text-sm">Obsidian vault</h3> <input placeholder="filter…" class="w-full mt-1 bg-transparent border-b border-border/40 outline-none text-[11px]"/></header> <!> <div class="flex-1 overflow-y-auto py-1"><!></div></aside> <section class="flex-1 flex flex-col min-w-0"><!></section></div>');function iu(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue(null),a=null,o=ue({"":!0}),l=ue(null),c=ue(""),u=ue(""),f=ue(""),h=ue(!1),d=ue(""),p=ue(""),m=ue(""),E=[],g=[];async function _(){try{const X=await MS();W(r,X.tree)}catch(X){W(p,`tree: ${String(X)}`)}}async function O(){try{a=await TS()}catch(X){W(p,`index: ${String(X)}`)}}async function D(X,K=!0){try{const se=await wS(X);K&&s(l)&&g.push(s(l)),W(l,X),W(u,se.abs_path),W(c,X.split("/").pop().replace(/\.(md|markdown)$/i,"")),W(d,se.content),W(f,se.rewritten),E.includes(X)||(E=[X,...E].slice(0,20)),W(p,""),y(X)}catch(se){mt({title:"Open failed",body:String(se).slice(0,160),kind:"err"})}}function y(X){const K=X.split("/"),se={...s(o)};let ne="";for(let N=0;N<K.length-1;N+=1)ne=ne?`${ne}/${K[N]}`:K[N],se[ne]=!0;W(o,se)}function B(X){W(o,{...s(o),[X]:!s(o)[X]})}function R(){const X=g.pop();X&&D(X,!1)}function C(X){var N;const K=X.target;if(!K)return;const se=K.closest("a");if(se){const V=se.getAttribute("href")??"";if(V.startsWith("obsidian://")){X.preventDefault();const re=decodeURIComponent(V.slice(11)),Me=AS(re,a,s(l));Me?D(Me):mt({title:"Wikilink not found",body:re,kind:"warn",ttlMs:2200});return}}const ne=K.closest(".code-copy-btn");if(ne){const V=rs(ne);if(V===null)return;(N=navigator.clipboard)==null||N.writeText(V).then(()=>{const re=ne.textContent;ne.textContent="Copied",ne.classList.add("copied"),setTimeout(()=>{ne.textContent=re??"Copy",ne.classList.remove("copied")},1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500}))}}zt(()=>{_(),O()}),lt(()=>(s(r),s(m)),()=>{W(t,(()=>{if(!s(r))return null;const X=s(m).trim().toLowerCase();if(!X)return s(r);function K(se){if(se.kind!=="dir")return se.name.toLowerCase().includes(X)?se:null;const ne=(se.children??[]).map(K).filter(N=>N!==null);return ne.length===0?null:{...se,children:ne}}return K(s(r))})())}),Ht(),wt();var b=OS(),A=M(b),k=M(A),z=U(M(k),2);gn(z),S(k);var H=U(k,2);{var q=X=>{var K=IS(),se=M(K,!0);S(K),me(()=>ee(se,s(p))),j(X,K)};Ae(H,X=>{s(p)&&X(q)})}var Q=U(H,2),G=M(Q);{var T=X=>{var K=Ai(),se=Pt(K);ct(se,1,()=>(s(t),L(()=>s(t).children??[])),ne=>ne.path,(ne,N)=>{dp(ne,{get node(){return s(N)},get openFolders(){return s(o)},get currentPath(){return s(l)},toggle:B,pick:D,depth:0})}),j(X,K)},w=X=>{var K=NS();j(X,K)};Ae(G,X=>{s(t)?X(T):X(w,-1)})}S(Q),S(A);var I=U(A,2),F=M(I);{var Y=X=>{var K=kS(),se=Pt(K),ne=M(se),N=M(ne),V=M(N,!0);S(N);var re=U(N,2),Me=M(re,!0);S(re),S(ne);var fe=U(ne,2),oe=M(fe);{var ve=Ne=>{var Oe=PS();Re("click",Oe,R),j(Ne,Oe)};Ae(oe,Ne=>{L(()=>g.length>0)&&Ne(ve)})}var ye=U(oe,2),Ie=U(ye,2);let be;var ke=M(Ie,!0);S(Ie),S(fe),S(se);var xe=U(se,2),Ee=M(xe);{var _e=Ne=>{var Oe=LS(),J=M(Oe,!0);S(Oe),me(()=>ee(J,s(d))),j(Ne,Oe)},De=Ne=>{var Oe=DS();es(Oe,()=>(tt(Yn),s(f),L(()=>Yn(s(f)))),!0),S(Oe),Re("click",Oe,C),j(Ne,Oe)};Ae(Ee,Ne=>{s(h)?Ne(_e):Ne(De,-1)})}S(xe),me(()=>{ee(V,s(c)),ee(Me,s(l)),be=vt(Ie,1,"text-[10px] px-2 py-0.5 border border-border/60 rounded",null,be,{"bg-accent":s(h),"text-bg":s(h)}),ee(ke,s(h)?"rendered":"raw")}),Re("click",ye,()=>gr({appId:"editor",kind:"Editor",title:s(c),props:{path:s(u)}})),Re("click",Ie,()=>W(h,!s(h))),j(X,K)},te=X=>{var K=US();j(X,K)};Ae(F,X=>{s(l)?X(Y):X(te,-1)})}S(I),S(b),nn(z,()=>s(m),X=>W(m,X)),j(n,b),Tt()}var FS=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"><strong>Editor error:</strong> </div>'),BS=ie('<button class="text-[10px] px-2 py-0.5 border border-border/60 text-muted rounded">Revert</button>'),zS=ie('<p class="text-muted px-3 py-1"> </p>'),HS=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="flex items-center gap-2 px-3 py-1.5 border-b border-border/40"><button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">Open…</button> <span class="text-fg truncate"> </span> <span class="text-muted text-[10px]"> </span> <div class="ml-auto flex gap-1"><!> <button title="Ctrl+S"> </button></div></header> <!> <div class="flex-1 min-h-0"></div></div>');function ru(n,e){var ne;Mt(e,!1);const t=ue(),i=ue();let r=ft(e,"app",8),a=ue(),o=ue(!1),l=ue(((ne=r().props)==null?void 0:ne.path)??""),c=ue(""),u=ue(""),f=ue(!1),h=ue(!1),d=ue(""),p=ue("plaintext"),m=null,E=null;const g={ts:"typescript",tsx:"typescript",js:"javascript",jsx:"javascript",svelte:"html",html:"html",xml:"xml",json:"json",yaml:"yaml",yml:"yaml",sh:"shell",bash:"shell",zsh:"shell",css:"css",scss:"scss",py:"python",rb:"ruby",rs:"rust",go:"go",java:"java",cpp:"cpp",c:"c",sql:"sql",md:"markdown",markdown:"markdown",ini:"ini",toml:"ini",dockerfile:"dockerfile"};function _(N){var Me;if(!N)return"plaintext";const V=N.split("/").pop();if(/^Dockerfile/i.test(V))return"dockerfile";const re=((Me=V.split(".").pop())==null?void 0:Me.toLowerCase())??"";return g[re]??"plaintext"}function O(N){N.editor.defineTheme("catppuccin-mocha",{base:"vs-dark",inherit:!0,rules:[{token:"comment",foreground:"6c7086",fontStyle:"italic"},{token:"keyword",foreground:"cba6f7"},{token:"string",foreground:"a6e3a1"},{token:"number",foreground:"fab387"},{token:"type",foreground:"f9e2af"},{token:"function",foreground:"89b4fa"},{token:"variable",foreground:"cdd6f4"}],colors:{"editor.background":"#1e1e2e","editor.foreground":"#cdd6f4","editorLineNumber.foreground":"#6c7086","editorLineNumber.activeForeground":"#cba6f7","editorCursor.foreground":"#89b4fa","editor.selectionBackground":"#45475a","editorWhitespace.foreground":"#313244","editor.lineHighlightBackground":"#313244","editorIndentGuide.background":"#313244","editorIndentGuide.activeBackground":"#45475a"}})}async function D(){if(!s(a))return;const N=window;if(!N.MonacoEnvironment){const V=new URL("data:text/javascript;base64,aW1wb3J0IHsgaW5pdGlhbGl6ZSB9IGZyb20gJy4uLy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKaW1wb3J0IHsgSlNPTldvcmtlciB9IGZyb20gJy4vanNvbldvcmtlci5qcyc7CgpzZWxmLm9ubWVzc2FnZSA9ICgpID0+IHsKICBpbml0aWFsaXplKChjdHgsIGNyZWF0ZURhdGEpID0+IHsKICAgIHJldHVybiBuZXcgSlNPTldvcmtlcihjdHgsIGNyZWF0ZURhdGEpOwogIH0pOwp9Owo=",import.meta.url),re=new URL("data:text/javascript;base64,aW1wb3J0IHsgaW5pdGlhbGl6ZSB9IGZyb20gJy4uLy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKaW1wb3J0IHsgQ1NTV29ya2VyIH0gZnJvbSAnLi9jc3NXb3JrZXIuanMnOwoKc2VsZi5vbm1lc3NhZ2UgPSAoKSA9PiB7CiAgaW5pdGlhbGl6ZSgoY3R4LCBjcmVhdGVEYXRhKSA9PiB7CiAgICByZXR1cm4gbmV3IENTU1dvcmtlcihjdHgsIGNyZWF0ZURhdGEpOwogIH0pOwp9Owo=",import.meta.url),Me=new URL("data:text/javascript;base64,aW1wb3J0IHsgaW5pdGlhbGl6ZSB9IGZyb20gJy4uLy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKaW1wb3J0IHsgSFRNTFdvcmtlciB9IGZyb20gJy4vaHRtbFdvcmtlci5qcyc7CgpzZWxmLm9ubWVzc2FnZSA9ICgpID0+IHsKICBpbml0aWFsaXplKChjdHgsIGNyZWF0ZURhdGEpID0+IHsKICAgIHJldHVybiBuZXcgSFRNTFdvcmtlcihjdHgsIGNyZWF0ZURhdGEpOwogIH0pOwp9Owo=",import.meta.url),fe=new URL("data:text/javascript;base64,aW1wb3J0IHsgaW5pdGlhbGl6ZSB9IGZyb20gJy4uLy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKaW1wb3J0ICogYXMgdHlwZXNjcmlwdFNlcnZpY2VzIGZyb20gJy4vbGliL3R5cGVzY3JpcHRTZXJ2aWNlcy5qcyc7CmV4cG9ydCB7IHR5cGVzY3JpcHRTZXJ2aWNlcyBhcyB0cyB9OwppbXBvcnQgeyBjcmVhdGUgfSBmcm9tICcuL3RzV29ya2VyLmpzJzsKZXhwb3J0IHsgVHlwZVNjcmlwdFdvcmtlciB9IGZyb20gJy4vdHNXb3JrZXIuanMnOwpleHBvcnQgeyBsaWJGaWxlTWFwIH0gZnJvbSAnLi9saWIvbGliLmpzJzsKCnNlbGYub25tZXNzYWdlID0gKCkgPT4gewogIGluaXRpYWxpemUoKGN0eCwgY3JlYXRlRGF0YSkgPT4gewogICAgcmV0dXJuIGNyZWF0ZShjdHgsIGNyZWF0ZURhdGEpOwogIH0pOwp9OwoKZXhwb3J0IHsgY3JlYXRlLCBpbml0aWFsaXplIH07Cg==",import.meta.url),oe=new URL("data:text/javascript;base64,aW1wb3J0IHsgaXNXb3JrZXJJbml0aWFsaXplZCB9IGZyb20gJy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKZXhwb3J0IHsgaW5pdGlhbGl6ZSB9IGZyb20gJy4uL2NvbW1vbi9pbml0aWFsaXplLmpzJzsKaW1wb3J0IHsgc3RhcnQgfSBmcm9tICcuL2VkaXRvci53b3JrZXIuc3RhcnQuanMnOwoKc2VsZi5vbm1lc3NhZ2UgPSAoKSA9PiB7CiAgaWYgKCFpc1dvcmtlckluaXRpYWxpemVkKCkpIHsKICAgIHN0YXJ0KCgpID0+IHsKICAgICAgcmV0dXJuIHt9OwogICAgfSk7CiAgfQp9Owo=",import.meta.url);N.MonacoEnvironment={getWorker(ve,ye){switch(ye){case"json":return new Worker(V,{type:"module"});case"css":case"scss":case"less":return new Worker(re,{type:"module"});case"html":case"handlebars":case"razor":return new Worker(Me,{type:"module"});case"typescript":case"javascript":return new Worker(fe,{type:"module"});default:return new Worker(oe,{type:"module"})}}}}m=await Pa(()=>import("../chunks/V3Cqym1g.js").then(V=>V.b),__vite__mapDeps([1,2,3,4,5])),O(m),E=m.editor.create(s(a),{value:s(u),language:s(p),theme:"catppuccin-mocha",automaticLayout:!0,minimap:{enabled:!1},scrollBeyondLastLine:!1,fontFamily:"JetBrains Mono, ui-monospace, monospace",fontSize:13,lineNumbers:"on",tabSize:2}),E.onDidChangeModelContent(()=>{E&&W(u,E.getValue())}),E.addCommand(m.KeyMod.CtrlCmd|m.KeyCode.KeyS,()=>{B()}),W(o,!0),s(l)&&await y(s(l))}async function y(N){if(N){W(f,!0),W(d,"");try{const V=await up(N);if(W(c,V.content),W(u,V.content),W(l,N),W(p,_(N)),m&&E){const re=E.getModel();re&&m.editor.setModelLanguage(re,s(p)),E.setValue(s(u))}}catch(V){W(d,String(V)),mt({title:"Load failed",body:s(d).slice(0,160),kind:"err"})}finally{W(f,!1)}}}async function B(){if(!s(l)){mt({title:"No path — open a file first",kind:"warn",ttlMs:1600});return}W(h,!0);try{await dt("/zeus-os/fs/write",{method:"POST",body:JSON.stringify({path:s(l),content:s(u)})}),W(c,s(u)),mt({title:"Saved",body:s(l).split("/").pop(),kind:"ok",ttlMs:1500})}catch(N){mt({title:"Save failed",body:String(N).slice(0,200),kind:"err"})}finally{W(h,!1)}}function R(){W(u,s(c)),E&&E.setValue(s(c))}async function C(){const N=window.prompt("Path to open:",s(l)||"/app/zeus/CLAUDE.md");N&&(await vr(),await y(N))}zt(()=>{D()}),Jt(()=>{try{E==null||E.dispose()}catch{}}),lt(()=>(s(o),tt(r()),s(l)),()=>{var N;if(s(o)&&r()&&((N=r().props)!=null&&N.path)&&r().props.path!==s(l)){const V=r().props.path;y(V)}}),lt(()=>(s(u),s(c)),()=>{W(t,s(u)!==s(c))}),lt(()=>s(l),()=>{W(i,s(l)?s(l).split("/").pop():"(unsaved)")}),Ht(),wt();var b=HS(),A=M(b);{var k=N=>{var V=FS(),re=U(M(V));S(V),me(()=>ee(re,` ${s(d)??""}`)),j(N,V)};Ae(A,N=>{s(d)&&N(k)})}var z=U(A,2),H=M(z),q=U(H,2),Q=M(q);S(q);var G=U(q,2),T=M(G,!0);S(G);var w=U(G,2),I=M(w);{var F=N=>{var V=BS();Re("click",V,R),j(N,V)};Ae(I,N=>{s(t)&&N(F)})}var Y=U(I,2),te=M(Y,!0);S(Y),S(w),S(z);var X=U(z,2);{var K=N=>{var V=zS(),re=M(V);S(V),me(()=>ee(re,`loading ${s(l)??""}…`)),j(N,V)};Ae(X,N=>{s(f)&&N(K)})}var se=U(X,2);Er(se,N=>W(a,N),()=>s(a)),S(b),me(()=>{$t(q,"title",s(l)),ee(Q,`${s(i)??""}${s(t)?" •":""}`),ee(T,s(p)),vt(Y,1,`text-[10px] px-2 py-0.5 rounded border ${s(t)?"border-accent text-accent":"border-border/60 text-muted"}`),Y.disabled=s(h)||!s(l)||!s(t),ee(te,s(h)?"saving…":"Save")}),Re("click",H,C),Re("click",Y,B),j(n,b),Tt()}function GS(){return dt("/zeus-os/ha/config")}function VS(){return dt("/zeus-os/linear/status")}function Ld(n,e={}){return dt("/zeus-os/linear/query",{method:"POST",body:JSON.stringify({query:n,variables:e})})}const ta=new Map;function Dd(n,e,t,i){let r=ta.get(n);if(r&&r.url!==t){try{r.iframe.remove()}catch{}ta.delete(n),r=void 0}if(!r){const a=document.createElement("iframe");a.src=t,a.title=i,a.className="h-full w-full border-0",r={url:t,iframe:a},ta.set(n,r)}r.iframe.parentElement!==e&&e.appendChild(r.iframe)}function WS(n,e){const t=ta.get(n);!t||!e||t.iframe.parentElement===e&&e.removeChild(t.iframe)}Rc(n=>{const e=ta.get(n);if(e){try{e.iframe.remove()}catch{}ta.delete(n)}});var $S=ie('<span class="text-[10px] px-1.5 py-0.5 rounded bg-ok/20 text-ok" title="Routed through Zeus reverse proxy with CF Access service-token headers">proxy · CF token</span> <span class="text-muted text-[10px] truncate"> </span>',1),XS=ie('<span class="text-muted text-[10px] truncate"> </span>'),qS=ie('<button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded">open ↗</button>'),YS=ie('<div class="px-3 py-2 border-b border-border/40 flex items-center gap-2 bg-surface2/30"><input placeholder="https://homeassistant.…" class="flex-1 bg-transparent border-b border-border/40 outline-none text-fg"/> <button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded">set</button> <span class="text-muted text-[10px]">runtime-only · persistent change requires ZEUS_OS_HA_URL in .env</span></div>'),KS=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"> </div>'),ZS=ie('<p class="text-muted px-3 py-2">loading…</p>'),JS=ie('<div class="flex-1 min-h-0 w-full"></div>'),QS=ie('<div class="flex-1 grid place-items-center text-muted text-center px-6"><div><p>No Home Assistant URL configured.</p> <p class="text-[10px] mt-2">Set <code class="text-fg">ZEUS_OS_HA_URL</code> in <code class="text-fg">zeus/.env</code> and restart zeus-core, or use "change url" above for a one-session override.</p></div></div>'),jS=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2"><h3 class="text-accent text-sm">Home Assistant</h3> <!> <div class="ml-auto flex gap-1"><button class="text-[10px] px-2 py-0.5 border border-border/60 rounded"> </button> <!></div></header> <!> <!> <!></div>');function au(n,e){Mt(e,!1);const t=ue();let i=ft(e,"app",8),r=ue(""),a=ue("direct"),o=ue(""),l=ue(""),c=ue(!0),u=ue(!1),f=ue(""),h=ue();async function d(){W(c,!0);try{const T=await GS();W(r,T.url),W(a,T.mode??"direct"),W(o,T.upstream??T.url),W(f,s(o)),W(l,"")}catch(T){W(l,String(T))}finally{W(c,!1)}}zt(async()=>{await d(),await vr(),s(h)&&s(r)&&Dd(i().instanceId,s(h),s(r),"Home Assistant")}),Jt(()=>{WS(i().instanceId,s(h))}),s(t);function p(){const T=s(a)==="proxy"?s(o):s(r);T&&window.open(T,"_blank","noopener")}lt(()=>(s(h),s(r),tt(i())),()=>{s(h)&&s(r)&&Dd(i().instanceId,s(h),s(r),"Home Assistant")}),lt(()=>s(r),()=>{W(t,(()=>{if(!s(r)||typeof window>"u")return!1;try{return new URL(s(r),window.location.href).origin===window.location.origin}catch{return!1}})())}),Ht(),wt();var m=jS(),E=M(m),g=U(M(E),2);{var _=T=>{var w=$S(),I=U(Pt(w),2),F=M(I);S(I),me(()=>ee(F,`→ ${s(o)??""}`)),j(T,w)},O=T=>{var w=XS(),I=M(w,!0);S(w),me(()=>ee(I,s(r)||"(no url configured)")),j(T,w)};Ae(g,T=>{s(a)==="proxy"?T(_):T(O,-1)})}var D=U(g,2),y=M(D),B=M(y,!0);S(y);var R=U(y,2);{var C=T=>{var w=qS();Re("click",w,p),j(T,w)};Ae(R,T=>{s(r)&&T(C)})}S(D),S(E);var b=U(E,2);{var A=T=>{var w=YS(),I=M(w);gn(I);var F=U(I,2);kn(2),S(w),nn(I,()=>s(f),Y=>W(f,Y)),Re("click",F,()=>{W(r,s(f)),W(u,!1)}),j(T,w)};Ae(b,T=>{s(u)&&T(A)})}var k=U(b,2);{var z=T=>{var w=KS(),I=M(w,!0);S(w),me(()=>ee(I,s(l))),j(T,w)};Ae(k,T=>{s(l)&&T(z)})}var H=U(k,2);{var q=T=>{var w=ZS();j(T,w)},Q=T=>{var w=JS();Er(w,I=>W(h,I),()=>s(h)),j(T,w)},G=T=>{var w=QS();j(T,w)};Ae(H,T=>{s(c)?T(q):s(r)?T(Q,1):T(G,-1)})}S(m),me(()=>ee(B,s(u)?"cancel":"change url")),Re("click",y,()=>W(u,!s(u))),j(n,m),Tt()}var ey=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"> </div>'),ty=ie(`<div class="flex-1 grid place-items-center text-muted text-center px-6"><div><p class="text-fg mb-2">Linear API key not configured.</p> <p class="text-[11px] leading-relaxed">Add <code class="text-accent">LINEAR_API_KEY</code> to <code class="text-fg">zeus/.env</code> (Linear → Settings → API → Personal API key), then restart zeus-core. The team key defaults
          to <code class="text-fg">LAB</code> — override with <code class="text-fg">ZEUS_LINEAR_TEAM_KEY</code>.</p></div></div>`),kd=ie("<option> </option>"),ny=ie('<li><button class="w-full text-left px-3 py-2 hover:bg-surface2/60"><div class="flex items-center justify-between"><span class="text-muted text-[10px]"> </span> <span class="text-[10px] px-1.5 rounded"> </span></div> <p class="text-fg mt-0.5 leading-snug"> </p> <div class="flex items-center justify-between mt-1 text-[10px] text-muted"><span> </span> <span> </span></div></button></li>'),iy=ie('<li class="px-3 py-6 text-muted text-center"> </li>'),Ud=ie('<span class="text-muted"> </span>'),ry=ie('<span class="text-[10px] px-1.5 rounded"> </span>'),ay=ie('<div class="flex gap-1 mt-2 flex-wrap"></div>'),sy=ie('<div class="prose-chat leading-relaxed" role="presentation"></div>'),oy=ie('<p class="text-muted text-[11px]">(no description)</p>'),ly=ie('<header class="mb-2"><a target="_blank" rel="noopener" class="text-muted text-[10px]"> </a> <h3 class="text-accent text-sm mt-1"> </h3> <div class="flex items-center gap-2 text-[10px] mt-1"><span> </span> <span class="text-muted"> </span> <!> <!></div> <!></header> <!> <p class="text-muted text-[10px] mt-4"> </p>',1),cy=ie('<p class="text-muted text-center mt-12">Pick an issue to read its description.</p>'),uy=ie('<header class="px-3 py-2 border-b border-border/40 flex items-center gap-2 flex-wrap"><h3 class="text-accent text-sm"> </h3> <input placeholder="title contains…" class="flex-1 min-w-[140px] bg-transparent border-b border-border/40 outline-none text-fg"/> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"><option>all states</option><!></select> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"><option>all projects</option><!></select> <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded">refresh</button> <span class="text-[10px] text-muted"> </span></header> <div class="flex-1 flex min-h-0"><ul class="w-1/2 overflow-y-auto border-r border-border/40"></ul> <section class="w-1/2 overflow-y-auto p-3"><!></section></div>',1),dy=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <!></div>');function su(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue(!1),r=ue("LAB"),a=ue([]),o=ue([]),l=ue([]),c=ue(""),u=ue(""),f=ue(""),h=ue(!1),d=ue(""),p=ue(""),m=ue(null);const E=`query Issues($filter: IssueFilter!) {
    issues(filter: $filter, first: 50, orderBy: updatedAt) {
      nodes {
        id identifier title description url priority createdAt updatedAt
        state { id name color type }
        assignee { displayName }
        project { id name }
        labels { nodes { name color } }
      }
    }
  }`,g=`query Meta($teamKey: String!) {
    teams(filter: { key: { eq: $teamKey } }) {
      nodes {
        id name key
        states { nodes { id name color type } }
      }
    }
    projects(first: 50) { nodes { id name } }
  }`;async function _(){try{const q=await VS();W(i,q.configured),W(r,q.team_key)}catch(q){W(d,String(q))}}async function O(){var q,Q,G,T;if(s(i))try{const w=await Ld(g,{teamKey:s(r)});if((q=w.errors)!=null&&q.length){W(d,w.errors.map(I=>I.message).join("; "));return}W(a,((G=(Q=w.data)==null?void 0:Q.teams.nodes[0])==null?void 0:G.states.nodes)??[]),W(o,((T=w.data)==null?void 0:T.projects.nodes)??[]),W(d,"")}catch(w){W(d,String(w))}}async function D(){var q,Q;if(s(i)){W(h,!0);try{const G={team:{key:{eq:s(r)}}};s(c)&&(G.state={id:{eq:s(c)}}),s(u)&&(G.project={id:{eq:s(u)}}),s(f).trim()&&(G.title={containsIgnoreCase:s(f).trim()});const T=await Ld(E,{filter:G});if((q=T.errors)!=null&&q.length){W(d,T.errors.map(w=>w.message).join("; "));return}W(l,((Q=T.data)==null?void 0:Q.issues.nodes)??[]),W(d,""),W(p,new Date().toLocaleTimeString())}catch(G){W(d,String(G))}finally{W(h,!1)}}}function y(q){if(!q)return"";try{return new Date(q).toLocaleDateString([],{month:"short",day:"numeric"})}catch{return q}}function B(q){return["no priority","urgent","high","medium","low"][q]??"?"}function R(q){var w;const Q=q.target;if(!Q)return;const G=Q.closest(".code-copy-btn");if(!G)return;const T=rs(G);T!==null&&((w=navigator.clipboard)==null||w.writeText(T).then(()=>{G.textContent="Copied",G.classList.add("copied"),setTimeout(()=>{G.textContent="Copy",G.classList.remove("copied")},1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500})))}zt(async()=>{await _(),s(i)&&(await O(),await D())}),wt();var C=dy(),b=M(C);{var A=q=>{var Q=ey(),G=M(Q,!0);S(Q),me(()=>ee(G,s(d))),j(q,Q)};Ae(b,q=>{s(d)&&q(A)})}var k=U(b,2);{var z=q=>{var Q=ty();j(q,Q)},H=q=>{var Q=uy(),G=Pt(Q),T=M(G),w=M(T);S(T);var I=U(T,2);gn(I);var F=U(I,2),Y=M(F);Y.value=Y.__value="";var te=U(Y);ct(te,1,()=>s(a),Ie=>Ie.id,(Ie,be)=>{var ke=kd(),xe=M(ke,!0);S(ke);var Ee={};me(()=>{ee(xe,(s(be),L(()=>s(be).name))),Ee!==(Ee=(s(be),L(()=>s(be).id)))&&(ke.value=(ke.__value=(s(be),L(()=>s(be).id)))??"")}),j(Ie,ke)}),S(F);var X=U(F,2),K=M(X);K.value=K.__value="";var se=U(K);ct(se,1,()=>s(o),Ie=>Ie.id,(Ie,be)=>{var ke=kd(),xe=M(ke,!0);S(ke);var Ee={};me(()=>{ee(xe,(s(be),L(()=>s(be).name))),Ee!==(Ee=(s(be),L(()=>s(be).id)))&&(ke.value=(ke.__value=(s(be),L(()=>s(be).id)))??"")}),j(Ie,ke)}),S(X);var ne=U(X,2),N=U(ne,2),V=M(N);S(N),S(G);var re=U(G,2),Me=M(re);ct(Me,5,()=>s(l),Ie=>Ie.id,(Ie,be)=>{var ke=ny();let xe;var Ee=M(ke),_e=M(Ee),De=M(_e),Ne=M(De,!0);S(De);var Oe=U(De,2),J=M(Oe,!0);S(Oe),S(_e);var We=U(_e,2),Fe=M(We,!0);S(We);var P=U(We,2),x=M(P),Z=M(x,!0);S(x);var ae=U(x,2),de=M(ae);S(ae),S(P),S(Ee),S(ke),me((Le,He)=>{var Se;xe=vt(ke,1,"border-b border-border/20",null,xe,{"bg-surface2":((Se=s(m))==null?void 0:Se.id)===s(be).id}),ee(Ne,(s(be),L(()=>s(be).identifier))),Ln(Oe,`background: ${s(be),L(()=>s(be).state.color)??""}33; color: ${s(be),L(()=>s(be).state.color)??""};`),ee(J,(s(be),L(()=>s(be).state.name))),ee(Fe,(s(be),L(()=>s(be).title))),ee(Z,(s(be),L(()=>{var we;return((we=s(be).project)==null?void 0:we.name)??"(no project)"}))),ee(de,`${Le??""} · ${He??""}`)},[()=>(s(be),L(()=>B(s(be).priority))),()=>(s(be),L(()=>y(s(be).updatedAt)))]),Re("click",Ee,()=>W(m,s(be))),j(Ie,ke)},Ie=>{var be=iy(),ke=M(be,!0);S(be),me(()=>ee(ke,s(h)?"loading…":"no issues match.")),j(Ie,be)}),S(Me);var fe=U(Me,2),oe=M(fe);{var ve=Ie=>{var be=ly(),ke=Pt(be),xe=M(ke),Ee=M(xe);S(xe);var _e=U(xe,2),De=M(_e,!0);S(_e);var Ne=U(_e,2),Oe=M(Ne),J=M(Oe);S(Oe);var We=U(Oe,2),Fe=M(We,!0);S(We);var P=U(We,2);{var x=Pe=>{var Ce=Ud(),qe=M(Ce);S(Ce),me(()=>ee(qe,`· ${s(m),L(()=>s(m).project.name)??""}`)),j(Pe,Ce)};Ae(P,Pe=>{s(m),L(()=>s(m).project)&&Pe(x)})}var Z=U(P,2);{var ae=Pe=>{var Ce=Ud(),qe=M(Ce);S(Ce),me(()=>ee(qe,`· ${s(m),L(()=>s(m).assignee.displayName)??""}`)),j(Pe,Ce)};Ae(Z,Pe=>{s(m),L(()=>s(m).assignee)&&Pe(ae)})}S(Ne);var de=U(Ne,2);{var Le=Pe=>{var Ce=ay();ct(Ce,5,()=>(s(m),L(()=>s(m).labels.nodes)),qe=>qe.name,(qe,je)=>{var st=ry(),ce=M(st,!0);S(st),me(()=>{Ln(st,`background: ${s(je),L(()=>s(je).color)??""}33; color: ${s(je),L(()=>s(je).color)??""};`),ee(ce,(s(je),L(()=>s(je).name)))}),j(qe,st)}),S(Ce),j(Pe,Ce)};Ae(de,Pe=>{s(m),L(()=>s(m).labels&&s(m).labels.nodes.length)&&Pe(Le)})}S(ke);var He=U(ke,2);{var Se=Pe=>{var Ce=sy();es(Ce,()=>(tt(Yn),s(m),L(()=>Yn(s(m).description))),!0),S(Ce),Re("click",Ce,R),j(Pe,Ce)},we=Pe=>{var Ce=oy();j(Pe,Ce)};Ae(He,Pe=>{s(m),L(()=>s(m).description)?Pe(Se):Pe(we,-1)})}var Ge=U(He,2),Je=M(Ge);S(Ge),me((Pe,Ce,qe)=>{$t(xe,"href",(s(m),L(()=>s(m).url))),ee(Ee,`${s(m),L(()=>s(m).identifier)??""} ↗`),ee(De,(s(m),L(()=>s(m).title))),Ln(Oe,`color: ${s(m),L(()=>s(m).state.color)??""};`),ee(J,`● ${s(m),L(()=>s(m).state.name)??""}`),ee(Fe,Pe),ee(Je,`created ${Ce??""} · updated ${qe??""}`)},[()=>(s(m),L(()=>B(s(m).priority))),()=>(s(m),L(()=>y(s(m).createdAt))),()=>(s(m),L(()=>y(s(m).updatedAt)))]),j(Ie,be)},ye=Ie=>{var be=cy();j(Ie,be)};Ae(oe,Ie=>{s(m)?Ie(ve):Ie(ye,-1)})}S(fe),S(re),me(()=>{ee(w,`Linear · ${s(r)??""}`),ee(V,`${s(l),L(()=>s(l).length)??""} ${s(h)?"loading…":""} ${s(p)??""}`)}),nn(I,()=>s(f),Ie=>W(f,Ie)),Re("keydown",I,Ie=>Ie.key==="Enter"&&D()),Ni(F,()=>s(c),Ie=>W(c,Ie)),Re("change",F,D),Ni(X,()=>s(u),Ie=>W(u,Ie)),Re("change",X,D),Re("click",ne,D),j(q,Q)};Ae(k,q=>{s(i)?q(H,-1):q(z)})}S(C),j(n,C),Tt()}function fy(n=40){return dt(`/zeus-os/sys/processes?limit=${n}`)}function hy(){return dt("/zeus-os/sys/network")}var py=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"> </div>'),my=ie('<tr class="border-t border-border/10 hover:bg-surface2/30"><td class="text-right pr-2 text-muted"> </td><td class="pr-2 text-fg"> </td><td class="text-right pr-2 text-fg"> </td><td class="text-right pr-2 text-muted"> </td><td class="text-right pr-2 text-muted"> </td><td class="text-fg/90 truncate max-w-[400px]"> </td></tr>'),gy=ie('<tr><td colspan="6" class="text-muted text-center py-6"> </td></tr>'),_y=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2 flex-wrap"><h3 class="text-accent text-sm">Processes</h3> <input placeholder="filter…" class="flex-1 min-w-[120px] bg-transparent border-b border-border/40 outline-none text-fg"/> <span class="text-muted text-[10px]"> </span></header> <div class="flex-1 overflow-y-auto"><table class="w-full"><thead class="text-muted text-[10px] uppercase sticky top-0 bg-bg/90 backdrop-blur"><tr><th>PID</th><th class="text-left pr-2">user</th><th>CPU%</th><th>MEM%</th><th>RSS</th><th class="text-left">command</th></tr></thead><tbody></tbody></table></div></div>');function ou(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue([]),a=ue(""),o=ue(""),l=ue(!0),c=null,u=ue(""),f=ue("pcpu");async function h(){try{const w=await fy(60);W(r,w.processes??[]),W(a,w.ok?"":w.error??""),W(o,new Date().toLocaleTimeString())}catch(w){W(a,String(w))}finally{W(l,!1)}}zt(()=>{h(),c=setInterval(h,4e3)}),Jt(()=>{c&&clearInterval(c)});function d(w){W(f,w)}lt(()=>(s(r),s(u),s(f)),()=>{W(t,s(r).filter(w=>{const I=s(u).toLowerCase().trim();return I?w.comm.toLowerCase().includes(I)||w.cmd.toLowerCase().includes(I)||w.user.toLowerCase().includes(I):!0}).slice().sort((w,I)=>{const F=w[s(f)],Y=I[s(f)];return s(f)==="pid"?F-Y:Y-F}))}),Ht(),wt();var p=_y(),m=M(p);{var E=w=>{var I=py(),F=M(I,!0);S(I),me(()=>ee(F,s(a))),j(w,I)};Ae(m,w=>{s(a)&&w(E)})}var g=U(m,2),_=U(M(g),2);gn(_);var O=U(_,2),D=M(O);S(O),S(g);var y=U(g,2),B=M(y),R=M(B),C=M(R),b=M(C);let A;var k=U(b,2);let z;var H=U(k);let q;var Q=U(H);let G;kn(),S(C),S(R);var T=U(R);ct(T,5,()=>s(t),w=>w.pid,(w,I)=>{var F=my(),Y=M(F),te=M(Y,!0);S(Y);var X=U(Y),K=M(X,!0);S(X);var se=U(X),ne=M(se,!0);S(se);var N=U(se),V=M(N,!0);S(N);var re=U(N),Me=M(re);S(re);var fe=U(re),oe=M(fe,!0);S(fe),S(F),me((ve,ye,Ie)=>{ee(te,(s(I),L(()=>s(I).pid))),ee(K,(s(I),L(()=>s(I).user))),ee(ne,ve),ee(V,ye),ee(Me,`${Ie??""} MB`),$t(fe,"title",(s(I),L(()=>s(I).cmd))),ee(oe,(s(I),L(()=>s(I).comm)))},[()=>(s(I),L(()=>s(I).pcpu.toFixed(1))),()=>(s(I),L(()=>s(I).pmem.toFixed(1))),()=>(s(I),L(()=>s(I).rss_mb.toFixed(0)))]),j(w,F)},w=>{var I=gy(),F=M(I),Y=M(F,!0);S(F),S(I),me(()=>ee(Y,s(l)?"loading…":"no processes match. Host SSH may not be configured (ZEUS_OS_PTY_HOST_SSH=0).")),j(w,I)}),S(T),S(B),S(y),S(p),me(()=>{ee(D,`${s(t),L(()=>s(t).length)??""} / ${s(r),L(()=>s(r).length)??""}${s(l)?" · loading…":""} ${s(o)??""}`),A=vt(b,1,"text-right pr-2 py-1 cursor-pointer",null,A,{"text-accent":s(f)==="pid"}),z=vt(k,1,"text-right pr-2 cursor-pointer",null,z,{"text-accent":s(f)==="pcpu"}),q=vt(H,1,"text-right pr-2 cursor-pointer",null,q,{"text-accent":s(f)==="pmem"}),G=vt(Q,1,"text-right pr-2 cursor-pointer",null,G,{"text-accent":s(f)==="rss_mb"})}),nn(_,()=>s(u),w=>W(u,w)),Re("click",b,()=>d("pid")),Re("click",k,()=>d("pcpu")),Re("click",H,()=>d("pmem")),Re("click",Q,()=>d("rss_mb")),j(n,p),Tt()}var vy=ie('<div class="bg-warn/15 border border-warn/30 rounded px-3 py-2 text-warn"> </div>'),xy=ie('<p class="text-fg"> <span class="text-muted">·</span> </p> <p class="text-muted text-[10px]"> </p>',1),by=ie('<p class="text-muted text-[11px]">Tailscale: not connected (or `tailscale status --json` unavailable).</p>'),Sy=ie('<tr class="border-t border-border/20"><td class="py-1"><span>●</span> <span class="text-fg ml-1"> </span></td><td class="py-1 text-fg/80"> </td><td class="py-1 text-muted"> </td><td class="py-1 text-right text-muted"> </td><td class="py-1 text-right text-muted"> </td><td class="py-1 text-right text-muted"> </td></tr>'),yy=ie('<table class="w-full"><thead class="text-muted text-[10px] text-left"><tr><th>Host</th><th>IP</th><th>OS</th><th class="text-right">RX</th><th class="text-right">TX</th><th class="text-right">seen</th></tr></thead><tbody></tbody></table>'),Ey=ie('<pre class="text-[10px] text-fg/80 whitespace-pre-wrap"> </pre>'),My=ie('<p class="text-muted text-[11px]">No peers reported.</p>'),Ty=ie('<tr class="border-t border-border/20"><td class="py-1 text-fg"> </td><td> </td><td class="py-1 text-fg/80"> </td><td class="py-1 text-muted text-[10px]"> </td><td class="py-1 text-right text-muted"> </td></tr>'),wy=ie('<table class="w-full"><thead class="text-muted text-[10px] text-left"><tr><th>Interface</th><th>State</th><th>Addrs</th><th>MAC</th><th class="text-right">MTU</th></tr></thead><tbody></tbody></table>'),Ay=ie('<p class="text-muted text-[11px]">No interface data.</p>'),Ry=ie('<section><h4 class="text-accent text-[11px] uppercase mb-1">This host</h4> <!></section> <section><h4 class="text-accent text-[11px] uppercase mb-1">Tailscale peers <span class="text-muted"> </span></h4> <!></section> <section><h4 class="text-accent text-[11px] uppercase mb-1">Local interfaces</h4> <!></section>',1),Cy=ie('<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-5"><!> <header><h3 class="text-accent text-sm">Network</h3> <p class="text-muted text-[10px]"> </p></header> <!></div>');function lu(n,e){Mt(e,!1);const t=ue(),i=ue();ft(e,"app",8)();let a=ue(null),o=ue(""),l=ue(""),c=null;async function u(){try{W(a,await hy()),W(o,s(a).tailscale.ok?"":s(a).tailscale.error??""),W(l,new Date().toLocaleTimeString())}catch(y){W(o,String(y))}}function f(y){return y?y<1024?`${y} B`:y<1048576?`${(y/1024).toFixed(0)} KB`:y<1073741824?`${(y/1048576).toFixed(1)} MB`:`${(y/1073741824).toFixed(2)} GB`:"0"}function h(y){if(!y)return"";try{const B=Date.now()-new Date(y).getTime(),R=Math.floor(B/1e3);return R<60?`${R}s ago`:R<3600?`${Math.floor(R/60)}m ago`:R<86400?`${Math.floor(R/3600)}h ago`:`${Math.floor(R/86400)}d ago`}catch{return y}}zt(()=>{u(),c=setInterval(u,1e4)}),Jt(()=>{c&&clearInterval(c)}),lt(()=>s(a),()=>{var y;W(t,((y=s(a))==null?void 0:y.tailscale.peers)??[])}),lt(()=>s(t),()=>{W(i,s(t).filter(y=>y.online).length)}),Ht(),wt();var d=Cy(),p=M(d);{var m=y=>{var B=vy(),R=M(B,!0);S(B),me(()=>ee(R,s(o))),j(y,B)};Ae(p,y=>{s(o)&&y(m)})}var E=U(p,2),g=U(M(E),2),_=M(g,!0);S(g),S(E);var O=U(E,2);{var D=y=>{var B=Ry(),R=Pt(B),C=U(M(R),2);{var b=X=>{var K=xy(),se=Pt(K),ne=M(se),N=U(ne,2);S(se);var V=U(se,2),re=M(V);S(V),me(()=>{ee(ne,`${s(a),L(()=>s(a).tailscale.self.hostname)??""} `),ee(N,` ${s(a),L(()=>s(a).tailscale.self.ip)??""}`),ee(re,`${s(a),L(()=>s(a).tailscale.self.dns_name)??""} · ${s(a),L(()=>s(a).tailscale.self.os)??""}`)}),j(X,K)},A=X=>{var K=by();j(X,K)};Ae(C,X=>{s(a),L(()=>{var K;return(K=s(a).tailscale.self)==null?void 0:K.ip})?X(b):X(A,-1)})}S(R);var k=U(R,2),z=M(k),H=U(M(z)),q=M(H);S(H),S(z);var Q=U(z,2);{var G=X=>{var K=yy(),se=U(M(K));ct(se,5,()=>s(t),ne=>ne.dns_name??ne.ip??ne.hostname,(ne,N)=>{var V=Sy(),re=M(V),Me=M(re);let fe;var oe=U(Me,2),ve=M(oe,!0);S(oe),S(re);var ye=U(re),Ie=M(ye,!0);S(ye);var be=U(ye),ke=M(be,!0);S(be);var xe=U(be),Ee=M(xe,!0);S(xe);var _e=U(xe),De=M(_e,!0);S(_e);var Ne=U(_e),Oe=M(Ne,!0);S(Ne),S(V),me((J,We,Fe)=>{fe=vt(Me,1,"",null,fe,{"text-ok":s(N).online,"text-muted":!s(N).online}),ee(ve,(s(N),L(()=>s(N).hostname??"?"))),ee(Ie,(s(N),L(()=>s(N).ip??"–"))),ee(ke,(s(N),L(()=>s(N).os??""))),ee(Ee,J),ee(De,We),ee(Oe,Fe)},[()=>(s(N),L(()=>f(s(N).rx_bytes))),()=>(s(N),L(()=>f(s(N).tx_bytes))),()=>(s(N),L(()=>s(N).online?"now":h(s(N).last_seen)))]),j(ne,V)}),S(se),S(K),j(X,K)},T=X=>{var K=Ey(),se=M(K,!0);S(K),me(ne=>ee(se,ne),[()=>(s(a),L(()=>s(a).tailscale.raw.slice(0,1200)))]),j(X,K)},w=X=>{var K=My();j(X,K)};Ae(Q,X=>{s(t),L(()=>s(t).length)?X(G):(s(a),L(()=>s(a).tailscale.raw)?X(T,1):X(w,-1))})}S(k);var I=U(k,2),F=U(M(I),2);{var Y=X=>{var K=wy(),se=U(M(K));ct(se,5,()=>(s(a),L(()=>s(a).interfaces)),ne=>ne.name,(ne,N)=>{var V=Ty(),re=M(V),Me=M(re,!0);S(re);var fe=U(re);let oe;var ve=M(fe,!0);S(fe);var ye=U(fe),Ie=M(ye,!0);S(ye);var be=U(ye),ke=M(be,!0);S(be);var xe=U(be),Ee=M(xe,!0);S(xe),S(V),me(_e=>{ee(Me,(s(N),L(()=>s(N).name))),oe=vt(fe,1,"py-1",null,oe,{"text-ok":s(N).state==="UP","text-muted":s(N).state!=="UP"}),ee(ve,(s(N),L(()=>s(N).state??""))),ee(Ie,_e),ee(ke,(s(N),L(()=>s(N).mac??""))),ee(Ee,(s(N),L(()=>s(N).mtu??"")))},[()=>(s(N),L(()=>s(N).addrs.join(", ")))]),j(ne,V)}),S(se),S(K),j(X,K)},te=X=>{var K=Ay();j(X,K)};Ae(F,X=>{s(a),L(()=>s(a).interfaces.length)?X(Y):X(te,-1)})}S(I),me(()=>ee(q,`(${s(i)??""} online / ${s(t),L(()=>s(t).length)??""})`)),j(y,B)};Ae(O,y=>{s(a)&&y(D)})}S(d),me(()=>ee(_,s(l)?`refreshed ${s(l)}`:"loading…")),j(n,d),Tt()}var Iy=ie('<textarea spellcheck="false" placeholder="Quick scratchpad. Markdown-aware preview. Persists per-window in localStorage; export to ~/.zeus/notepad-*.md when you want it on disk."></textarea>'),Ny=ie('<p class="text-muted">(empty)</p>'),Py=ie('<div role="presentation"><!></div>'),Ly=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2"><h3 class="text-accent text-sm">Notepad</h3> <span class="text-muted text-[10px]"> </span> <div class="ml-auto flex gap-1 text-[10px]"><button>edit</button> <button>split</button> <button>preview</button> <button class="px-2 py-0.5 border border-border/60 rounded text-muted hover:text-fg">export .md</button> <button class="px-2 py-0.5 border border-err/60 rounded text-err hover:bg-err hover:text-bg">clear</button></div></header> <div class="flex-1 flex min-h-0"><!> <!></div></div>');function cu(n,e){Mt(e,!1);const i=`zeus-os.notepad.${ft(e,"app",8)().instanceId}`,r=600;let a=ue(""),o=ue("edit"),l=ue(""),c=null;function u(){typeof localStorage>"u"||W(a,localStorage.getItem(i)??"")}function f(){if(!(typeof localStorage>"u"))try{localStorage.setItem(i,s(a)),W(l,new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"}))}catch{}}function h(){c&&clearTimeout(c),c=setTimeout(f,r)}async function d(){const I=`/root/.zeus/notepad-${new Date().toISOString().replace(/[:.]/g,"-").slice(0,19)}.md`;try{await dt("/zeus-os/fs/write",{method:"POST",body:JSON.stringify({path:I,content:s(a)})}),mt({title:"Exported",body:I,kind:"ok",ttlMs:2200})}catch(F){mt({title:"Export failed",body:String(F).slice(0,160),kind:"err"})}}function p(){(!s(a)||confirm("Clear notepad contents?"))&&(W(a,""),f())}function m(w){var te;const I=w.target;if(!I)return;const F=I.closest(".code-copy-btn");if(!F)return;const Y=rs(F);Y!==null&&((te=navigator.clipboard)==null||te.writeText(Y).then(()=>{F.textContent="Copied",F.classList.add("copied"),setTimeout(()=>{F.textContent="Copy",F.classList.remove("copied")},1200)},()=>mt({title:"Copy failed",kind:"warn",ttlMs:1500})))}zt(()=>{u()}),Jt(()=>{c&&clearTimeout(c),f()}),lt(()=>s(a),()=>{s(a)!==void 0&&h()}),Ht(),wt();var E=Ly(),g=M(E),_=U(M(g),2),O=M(_);S(_);var D=U(_,2),y=M(D);let B;var R=U(y,2);let C;var b=U(R,2);let A;var k=U(b,2),z=U(k,2);S(D),S(g);var H=U(g,2),q=M(H);{var Q=w=>{var I=Iy();fo(I),me(()=>vt(I,1,`flex-1 bg-transparent p-4 outline-none text-fg leading-relaxed resize-none ${s(o)==="split"?"border-r border-border/40 w-1/2":""}`)),nn(I,()=>s(a),F=>W(a,F)),j(w,I)};Ae(q,w=>{(s(o)==="edit"||s(o)==="split")&&w(Q)})}var G=U(q,2);{var T=w=>{var I=Py(),F=M(I);{var Y=K=>{var se=Ai(),ne=Pt(se);es(ne,()=>(tt(Yn),s(a),L(()=>Yn(s(a))))),j(K,se)},te=nr(()=>(s(a),L(()=>s(a).trim()))),X=K=>{var se=Ny();j(K,se)};Ae(F,K=>{s(te)?K(Y):K(X,-1)})}S(I),me(()=>vt(I,1,`flex-1 overflow-y-auto p-4 prose-chat leading-relaxed ${s(o)==="split"?"w-1/2":""}`)),Re("click",I,m),j(w,I)};Ae(G,w=>{(s(o)==="preview"||s(o)==="split")&&w(T)})}S(H),S(E),me(()=>{ee(O,`${s(a),L(()=>s(a).length)??""} chars${s(l)?` · saved ${s(l)}`:""}`),B=vt(y,1,"px-2 py-0.5 rounded border",null,B,{"border-accent":s(o)==="edit","text-accent":s(o)==="edit","border-border":s(o)!=="edit","text-muted":s(o)!=="edit"}),C=vt(R,1,"px-2 py-0.5 rounded border",null,C,{"border-accent":s(o)==="split","text-accent":s(o)==="split","border-border":s(o)!=="split","text-muted":s(o)!=="split"}),A=vt(b,1,"px-2 py-0.5 rounded border",null,A,{"border-accent":s(o)==="preview","text-accent":s(o)==="preview","border-border":s(o)!=="preview","text-muted":s(o)!=="preview"})}),Re("click",y,()=>W(o,"edit")),Re("click",R,()=>W(o,"split")),Re("click",b,()=>W(o,"preview")),Re("click",k,d),Re("click",z,p),j(n,E),Tt()}var Dy=ie('<div class="bg-warn/15 border-b border-warn/30 px-3 py-2 text-warn text-[11px]"> <p class="mt-1 text-[10px] text-muted">Calendar reads from ingested gcal facts — ensure ZEUS_GCAL_ENABLED is on and the gcal source has run via Iris.</p></div>'),ky=ie('<p class="text-muted text-[10px] mt-0.5"> </p>'),Uy=ie('<p class="text-fg/80 text-[11px] mt-1 line-clamp-2 whitespace-pre-wrap"> </p>'),Oy=ie('<p class="text-muted text-[10px] mt-1 italic"> </p>'),Fy=ie('<li class="border-b border-border/20 px-3 py-2"><div class="flex items-baseline justify-between gap-2"><span class="text-fg"> </span> <span class="text-muted text-[10px] whitespace-nowrap"> </span></div> <!> <!> <!></li>'),By=ie("<ul></ul>"),zy=ie(`<p class="text-muted text-center mt-12 px-6">Nothing on the calendar for today, or gcal hasn't been ingested. Trigger via the Ingest app → Google Calendar.</p>`),Hy=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><header class="px-3 py-2 border-b border-border/40 flex items-center gap-2"><h3 class="text-accent text-sm">Today</h3> <span class="text-muted text-[10px]"> </span> <span class="ml-auto text-muted text-[10px]"> </span></header> <!> <div class="flex-1 overflow-y-auto"><!></div></div>');function uu(n,e){Mt(e,!1);const t=ue();ft(e,"app",8)();let r=ue(null),a=ue(""),o=ue(!0),l=ue(""),c=null;async function u(){W(o,!0);try{W(r,await dt("/calendar/today")),W(a,s(r).error??""),W(l,new Date().toLocaleTimeString())}catch(C){W(a,String(C))}finally{W(o,!1)}}function f(C){if(!C)return"";try{const b=new Date(C);return Number.isNaN(b.getTime())?C:b.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}catch{return C}}zt(()=>{u(),c=setInterval(u,5*6e4)}),Jt(()=>{c&&clearInterval(c)}),lt(()=>s(r),()=>{var C;W(t,((C=s(r))==null?void 0:C.events)??[])}),Ht(),wt();var h=Hy(),d=M(h),p=U(M(d),2),m=M(p,!0);S(p);var E=U(p,2),g=M(E);S(E),S(d);var _=U(d,2);{var O=C=>{var b=Dy(),A=M(b);kn(),S(b),me(()=>ee(A,`${s(a)??""} `)),j(C,b)};Ae(_,C=>{s(a)&&C(O)})}var D=U(_,2),y=M(D);{var B=C=>{var b=By();ct(b,5,()=>s(t),$n,(A,k)=>{var z=Fy(),H=M(z),q=M(H),Q=M(q,!0);S(q);var G=U(q,2),T=M(G);S(G),S(H);var w=U(H,2);{var I=K=>{var se=ky(),ne=M(se);S(se),me(()=>ee(ne,`📍 ${s(k),L(()=>s(k).location)??""}`)),j(K,se)};Ae(w,K=>{s(k),L(()=>s(k).location)&&K(I)})}var F=U(w,2);{var Y=K=>{var se=Uy(),ne=M(se);S(se),me(N=>ee(ne,`${N??""}${s(k),L(()=>s(k).description.length>240?"…":"")??""}`),[()=>(s(k),L(()=>s(k).description.slice(0,240)))]),j(K,se)};Ae(F,K=>{s(k),L(()=>s(k).description)&&K(Y)})}var te=U(F,2);{var X=K=>{var se=Oy(),ne=M(se,!0);S(se),me(()=>ee(ne,(s(k),L(()=>s(k).source)))),j(K,se)};Ae(te,K=>{s(k),L(()=>s(k).source)&&K(X)})}S(z),me((K,se)=>{ee(Q,(s(k),L(()=>s(k).summary??"(untitled)"))),ee(T,`${K??""}${se??""}`)},[()=>(s(k),L(()=>f(s(k).start))),()=>(s(k),L(()=>s(k).end?` – ${f(s(k).end)}`:""))]),j(A,z)}),S(b),j(C,b)},R=C=>{var b=zy();j(C,b)};Ae(y,C=>{s(t),L(()=>s(t).length)?C(B):s(o)||C(R,1)})}S(D),S(h),me(()=>{ee(m,(s(r),L(()=>{var C;return((C=s(r))==null?void 0:C.date)??""}))),ee(g,`${s(t),L(()=>s(t).length)??""} events${s(o)?" · loading…":""} ${s(l)??""}`)}),j(n,h),Tt()}var Gy=ie('<div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err"> </div>'),Vy=ie("<option> </option>"),Wy=ie('<button class="text-[10px] px-2 py-0.5 rounded border border-border/40 text-muted hover:text-fg hover:border-accent"> </button>'),$y=ie('<div class="flex flex-wrap gap-1 mb-3"></div>'),Xy=ie('<button><div class="flex-1 grid place-items-center bg-surface2/30"><img class="max-h-full max-w-full object-contain" loading="lazy"/></div> <p class="text-[9px] text-muted truncate px-1 py-0.5 border-t border-border/30 bg-surface/60"> </p></button>'),qy=ie('<div class="grid gap-2" style="grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));"></div>'),Yy=ie('<p class="text-muted text-center mt-12">No images in this directory.</p>'),Ky=ie('<aside class="w-1/3 min-w-[260px] border-l border-border/40 flex flex-col"><header class="px-3 py-2 border-b border-border/40 text-[11px] text-accent truncate"> </header> <div class="flex-1 grid place-items-center p-3 bg-surface2/30"><img class="max-h-full max-w-full object-contain"/></div> <footer class="px-3 py-1.5 border-t border-border/40 text-[10px] text-muted truncate"> </footer></aside>'),Zy=ie('<div class="h-full w-full flex flex-col font-mono text-xs"><!> <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2"><button class="text-muted hover:text-fg" title="up">↑</button> <input class="flex-1 bg-transparent border-b border-border/40 outline-none text-fg"/> <select class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]"></select> <span class="text-muted text-[10px]"> </span></header> <div class="flex-1 flex min-h-0"><div class="flex-1 overflow-y-auto p-2"><!> <!></div> <!></div></div>');function du(n,e){Mt(e,!1);const t=ue(),i=ue();ft(e,"app",8)();const a=new Set(["png","jpg","jpeg","gif","webp","svg","avif"]);let o=ue([]),l=ue(""),c=ue([]),u=ue(""),f=ue(!0),h=ue(null),d=ue("");function p(K){const se=K.lastIndexOf(".");return se<0?"":K.slice(se+1).toLowerCase()}async function m(){try{const K=await lp();W(o,K.read_roots??[]),s(o).length&&!s(l)&&(W(l,s(o)[0]),W(d,s(l)),await E(s(l)))}catch(K){W(u,String(K))}finally{W(f,!1)}}async function E(K){W(u,""),W(f,!0);try{const se=await cp(K);W(l,se.path),W(d,se.path),W(c,se.entries)}catch(se){W(u,String(se)),W(c,[])}finally{W(f,!1)}}function g(K){const se=s(l).endsWith("/")?s(l)+K.name:s(l)+"/"+K.name;K.kind==="dir"&&E(se)}function _(){const K=s(l).replace(/\/+$/,"").split("/");K.length<=1||(K.pop(),E(K.join("/")||"/"))}function O(K){const se=s(l).endsWith("/")?s(l)+K:s(l)+"/"+K;return`/zeus-os/fs/raw?path=${encodeURIComponent(se)}`}function D(K){const se=s(l).endsWith("/")?s(l)+K.name:s(l)+"/"+K.name;W(h,{name:K.name,abs:se})}function y(K){return K<1024?`${K} B`:K<1048576?`${(K/1024).toFixed(1)} KB`:`${(K/1048576).toFixed(1)} MB`}zt(m),lt(()=>s(c),()=>{W(t,s(c).filter(K=>K.kind==="file"&&a.has(p(K.name))))}),lt(()=>s(c),()=>{W(i,s(c).filter(K=>K.kind==="dir"))}),Ht(),wt();var B=Zy(),R=M(B);{var C=K=>{var se=Gy(),ne=M(se,!0);S(se),me(()=>ee(ne,s(u))),j(K,se)};Ae(R,K=>{s(u)&&K(C)})}var b=U(R,2),A=M(b),k=U(A,2);gn(k);var z=U(k,2);ct(z,5,()=>s(o),K=>K,(K,se)=>{var ne=Vy(),N=M(ne,!0);S(ne);var V={};me(()=>{ee(N,s(se)),V!==(V=s(se))&&(ne.value=(ne.__value=s(se))??"")}),j(K,ne)}),S(z);var H=U(z,2),q=M(H);S(H),S(b);var Q=U(b,2),G=M(Q),T=M(G);{var w=K=>{var se=$y();ct(se,5,()=>s(i),ne=>ne.name,(ne,N)=>{var V=Wy(),re=M(V);S(V),me(()=>ee(re,`📁 ${s(N),L(()=>s(N).name)??""}`)),Re("click",V,()=>g(s(N))),j(ne,V)}),S(se),j(K,se)};Ae(T,K=>{s(i),L(()=>s(i).length)&&K(w)})}var I=U(T,2);{var F=K=>{var se=qy();ct(se,5,()=>s(t),ne=>ne.name,(ne,N)=>{var V=Xy();let re;var Me=M(V),fe=M(Me);S(Me);var oe=U(Me,2),ve=M(oe,!0);S(oe),S(V),me((ye,Ie)=>{var be;re=vt(V,1,"aspect-square rounded border border-border/40 hover:border-accent overflow-hidden flex flex-col",null,re,{"border-accent":((be=s(h))==null?void 0:be.name)===s(N).name}),$t(V,"title",`${s(N),L(()=>s(N).name)??""} · ${ye??""}`),$t(fe,"src",Ie),$t(fe,"alt",(s(N),L(()=>s(N).name))),ee(ve,(s(N),L(()=>s(N).name)))},[()=>(s(N),L(()=>y(s(N).size))),()=>(s(N),L(()=>O(s(N).name)))]),Re("click",V,()=>D(s(N))),j(ne,V)}),S(se),j(K,se)},Y=K=>{var se=Yy();j(K,se)};Ae(I,K=>{s(t),L(()=>s(t).length)?K(F):s(f)||K(Y,1)})}S(G);var te=U(G,2);{var X=K=>{var se=Ky(),ne=M(se),N=M(ne,!0);S(ne);var V=U(ne,2),re=M(V);S(V);var Me=U(V,2),fe=M(Me,!0);S(Me),S(se),me(oe=>{$t(ne,"title",(s(h),L(()=>s(h).abs))),ee(N,(s(h),L(()=>s(h).name))),$t(re,"src",oe),$t(re,"alt",(s(h),L(()=>s(h).name))),ee(fe,(s(h),L(()=>s(h).abs)))},[()=>(s(h),L(()=>`/zeus-os/fs/raw?path=${encodeURIComponent(s(h).abs)}`))]),j(K,se)};Ae(te,K=>{s(h)&&K(X)})}S(Q),S(B),me(()=>ee(q,`${s(t),L(()=>s(t).length)??""} images${s(f)?" · loading…":""}`)),Re("click",A,_),nn(k,()=>s(d),K=>W(d,K)),Re("keydown",k,K=>K.key==="Enter"&&E(s(d))),Ni(z,()=>s(l),K=>W(l,K)),Re("change",z,()=>E(s(l))),j(n,B),Tt()}/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const fu="185",Jy=0,Od=1,Qy=2,Vs=1,jy=2,Oa=3,ir=0,yn=1,oi=2,Ri=0,na=1,Fd=2,Bd=3,zd=4,eE=5,fr=100,tE=101,nE=102,iE=103,rE=104,aE=200,sE=201,oE=202,lE=203,Pl=204,Ll=205,cE=206,uE=207,dE=208,fE=209,hE=210,pE=211,mE=212,gE=213,_E=214,Dl=0,kl=1,Ul=2,sa=3,Ol=4,Fl=5,Bl=6,zl=7,fp=0,vE=1,xE=2,di=0,hp=1,pp=2,mp=3,hu=4,gp=5,_p=6,vp=7,xp=300,br=301,oa=302,zo=303,Ho=304,bo=306,Hl=1e3,wi=1001,Gl=1002,an=1003,bE=1004,xs=1005,fn=1006,Go=1007,pr=1008,In=1009,bp=1010,Sp=1011,Za=1012,pu=1013,mi=1014,ci=1015,ki=1016,mu=1017,gu=1018,Ja=1020,yp=35902,Ep=35899,Mp=1021,Tp=1022,Xn=1023,Ui=1026,mr=1027,wp=1028,_u=1029,Sr=1030,vu=1031,xu=1033,Ws=33776,$s=33777,Xs=33778,qs=33779,Vl=35840,Wl=35841,$l=35842,Xl=35843,ql=36196,Yl=37492,Kl=37496,Zl=37488,Jl=37489,ao=37490,Ql=37491,jl=37808,ec=37809,tc=37810,nc=37811,ic=37812,rc=37813,ac=37814,sc=37815,oc=37816,lc=37817,cc=37818,uc=37819,dc=37820,fc=37821,hc=36492,pc=36494,mc=36495,gc=36283,_c=36284,so=36285,vc=36286,SE=3200,Hd=0,yE=1,Ji="",Rn="srgb",oo="srgb-linear",lo="linear",Nt="srgb",Or=7680,Gd=519,EE=512,ME=513,TE=514,bu=515,wE=516,AE=517,Su=518,RE=519,Vd=35044,Wd="300 es",ui=2e3,Qa=2001;function CE(n){for(let e=n.length-1;e>=0;--e)if(n[e]>=65535)return!0;return!1}function co(n){return document.createElementNS("http://www.w3.org/1999/xhtml",n)}function IE(){const n=co("canvas");return n.style.display="block",n}const $d={};function Xd(...n){const e="THREE."+n.shift();console.log(e,...n)}function Ap(n){const e=n[0];if(typeof e=="string"&&e.startsWith("TSL:")){const t=n[1];t&&t.isStackTrace?n[0]+=" "+t.getLocation():n[1]='Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.'}return n}function ut(...n){n=Ap(n);const e="THREE."+n.shift();{const t=n[0];t&&t.isStackTrace?console.warn(t.getError(e)):console.warn(e,...n)}}function Rt(...n){n=Ap(n);const e="THREE."+n.shift();{const t=n[0];t&&t.isStackTrace?console.error(t.getError(e)):console.error(e,...n)}}function ia(...n){const e=n.join(" ");e in $d||($d[e]=!0,ut(...n))}function NE(n,e,t){return new Promise(function(i,r){function a(){switch(n.clientWaitSync(e,n.SYNC_FLUSH_COMMANDS_BIT,0)){case n.WAIT_FAILED:r();break;case n.TIMEOUT_EXPIRED:setTimeout(a,t);break;default:i()}}setTimeout(a,t)})}const PE={[Dl]:kl,[Ul]:Bl,[Ol]:zl,[sa]:Fl,[kl]:Dl,[Bl]:Ul,[zl]:Ol,[Fl]:sa};class Ar{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const i=this._listeners;i[e]===void 0&&(i[e]=[]),i[e].indexOf(t)===-1&&i[e].push(t)}hasEventListener(e,t){const i=this._listeners;return i===void 0?!1:i[e]!==void 0&&i[e].indexOf(t)!==-1}removeEventListener(e,t){const i=this._listeners;if(i===void 0)return;const r=i[e];if(r!==void 0){const a=r.indexOf(t);a!==-1&&r.splice(a,1)}}dispatchEvent(e){const t=this._listeners;if(t===void 0)return;const i=t[e.type];if(i!==void 0){e.target=this;const r=i.slice(0);for(let a=0,o=r.length;a<o;a++)r[a].call(this,e);e.target=null}}}const on=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],Vo=Math.PI/180,xc=180/Math.PI;function as(){const n=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,i=Math.random()*4294967295|0;return(on[n&255]+on[n>>8&255]+on[n>>16&255]+on[n>>24&255]+"-"+on[e&255]+on[e>>8&255]+"-"+on[e>>16&15|64]+on[e>>24&255]+"-"+on[t&63|128]+on[t>>8&255]+"-"+on[t>>16&255]+on[t>>24&255]+on[i&255]+on[i>>8&255]+on[i>>16&255]+on[i>>24&255]).toLowerCase()}function St(n,e,t){return Math.max(e,Math.min(t,n))}function LE(n,e){return(n%e+e)%e}function Wo(n,e,t){return(1-t)*n+t*e}function Ta(n,e){switch(e.constructor){case Float32Array:return n;case Uint32Array:return n/4294967295;case Uint16Array:return n/65535;case Uint8Array:return n/255;case Int32Array:return Math.max(n/2147483647,-1);case Int16Array:return Math.max(n/32767,-1);case Int8Array:return Math.max(n/127,-1);default:throw new Error("THREE.MathUtils: Invalid component type.")}}function Sn(n,e){switch(e.constructor){case Float32Array:return n;case Uint32Array:return Math.round(n*4294967295);case Uint16Array:return Math.round(n*65535);case Uint8Array:return Math.round(n*255);case Int32Array:return Math.round(n*2147483647);case Int16Array:return Math.round(n*32767);case Int8Array:return Math.round(n*127);default:throw new Error("THREE.MathUtils: Invalid component type.")}}const Ru=class Ru{constructor(e=0,t=0){this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("THREE.Vector2: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("THREE.Vector2: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,i=this.y,r=e.elements;return this.x=r[0]*t+r[3]*i+r[6],this.y=r[1]*t+r[4]*i+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=St(this.x,e.x,t.x),this.y=St(this.y,e.y,t.y),this}clampScalar(e,t){return this.x=St(this.x,e,t),this.y=St(this.y,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(St(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const i=this.dot(e)/t;return Math.acos(St(i,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,i=this.y-e.y;return t*t+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const i=Math.cos(t),r=Math.sin(t),a=this.x-e.x,o=this.y-e.y;return this.x=a*i-o*r+e.x,this.y=a*r+o*i+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}};Ru.prototype.isVector2=!0;let xt=Ru;class ha{constructor(e=0,t=0,i=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=i,this._w=r}static slerpFlat(e,t,i,r,a,o,l){let c=i[r+0],u=i[r+1],f=i[r+2],h=i[r+3],d=a[o+0],p=a[o+1],m=a[o+2],E=a[o+3];if(h!==E||c!==d||u!==p||f!==m){let g=c*d+u*p+f*m+h*E;g<0&&(d=-d,p=-p,m=-m,E=-E,g=-g);let _=1-l;if(g<.9995){const O=Math.acos(g),D=Math.sin(O);_=Math.sin(_*O)/D,l=Math.sin(l*O)/D,c=c*_+d*l,u=u*_+p*l,f=f*_+m*l,h=h*_+E*l}else{c=c*_+d*l,u=u*_+p*l,f=f*_+m*l,h=h*_+E*l;const O=1/Math.sqrt(c*c+u*u+f*f+h*h);c*=O,u*=O,f*=O,h*=O}}e[t]=c,e[t+1]=u,e[t+2]=f,e[t+3]=h}static multiplyQuaternionsFlat(e,t,i,r,a,o){const l=i[r],c=i[r+1],u=i[r+2],f=i[r+3],h=a[o],d=a[o+1],p=a[o+2],m=a[o+3];return e[t]=l*m+f*h+c*p-u*d,e[t+1]=c*m+f*d+u*h-l*p,e[t+2]=u*m+f*p+l*d-c*h,e[t+3]=f*m-l*h-c*d-u*p,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,i,r){return this._x=e,this._y=t,this._z=i,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const i=e._x,r=e._y,a=e._z,o=e._order,l=Math.cos,c=Math.sin,u=l(i/2),f=l(r/2),h=l(a/2),d=c(i/2),p=c(r/2),m=c(a/2);switch(o){case"XYZ":this._x=d*f*h+u*p*m,this._y=u*p*h-d*f*m,this._z=u*f*m+d*p*h,this._w=u*f*h-d*p*m;break;case"YXZ":this._x=d*f*h+u*p*m,this._y=u*p*h-d*f*m,this._z=u*f*m-d*p*h,this._w=u*f*h+d*p*m;break;case"ZXY":this._x=d*f*h-u*p*m,this._y=u*p*h+d*f*m,this._z=u*f*m+d*p*h,this._w=u*f*h-d*p*m;break;case"ZYX":this._x=d*f*h-u*p*m,this._y=u*p*h+d*f*m,this._z=u*f*m-d*p*h,this._w=u*f*h+d*p*m;break;case"YZX":this._x=d*f*h+u*p*m,this._y=u*p*h+d*f*m,this._z=u*f*m-d*p*h,this._w=u*f*h-d*p*m;break;case"XZY":this._x=d*f*h-u*p*m,this._y=u*p*h-d*f*m,this._z=u*f*m+d*p*h,this._w=u*f*h+d*p*m;break;default:ut("Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const i=t/2,r=Math.sin(i);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(i),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,i=t[0],r=t[4],a=t[8],o=t[1],l=t[5],c=t[9],u=t[2],f=t[6],h=t[10],d=i+l+h;if(d>0){const p=.5/Math.sqrt(d+1);this._w=.25/p,this._x=(f-c)*p,this._y=(a-u)*p,this._z=(o-r)*p}else if(i>l&&i>h){const p=2*Math.sqrt(1+i-l-h);this._w=(f-c)/p,this._x=.25*p,this._y=(r+o)/p,this._z=(a+u)/p}else if(l>h){const p=2*Math.sqrt(1+l-i-h);this._w=(a-u)/p,this._x=(r+o)/p,this._y=.25*p,this._z=(c+f)/p}else{const p=2*Math.sqrt(1+h-i-l);this._w=(o-r)/p,this._x=(a+u)/p,this._y=(c+f)/p,this._z=.25*p}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let i=e.dot(t)+1;return i<1e-8?(i=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=i):(this._x=0,this._y=-e.z,this._z=e.y,this._w=i)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=i),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(St(this.dot(e),-1,1)))}rotateTowards(e,t){const i=this.angleTo(e);if(i===0)return this;const r=Math.min(1,t/i);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const i=e._x,r=e._y,a=e._z,o=e._w,l=t._x,c=t._y,u=t._z,f=t._w;return this._x=i*f+o*l+r*u-a*c,this._y=r*f+o*c+a*l-i*u,this._z=a*f+o*u+i*c-r*l,this._w=o*f-i*l-r*c-a*u,this._onChangeCallback(),this}slerp(e,t){let i=e._x,r=e._y,a=e._z,o=e._w,l=this.dot(e);l<0&&(i=-i,r=-r,a=-a,o=-o,l=-l);let c=1-t;if(l<.9995){const u=Math.acos(l),f=Math.sin(u);c=Math.sin(c*u)/f,t=Math.sin(t*u)/f,this._x=this._x*c+i*t,this._y=this._y*c+r*t,this._z=this._z*c+a*t,this._w=this._w*c+o*t,this._onChangeCallback()}else this._x=this._x*c+i*t,this._y=this._y*c+r*t,this._z=this._z*c+a*t,this._w=this._w*c+o*t,this.normalize();return this}slerpQuaternions(e,t,i){return this.copy(e).slerp(t,i)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),i=Math.random(),r=Math.sqrt(1-i),a=Math.sqrt(i);return this.set(r*Math.sin(e),r*Math.cos(e),a*Math.sin(t),a*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}const Cu=class Cu{constructor(e=0,t=0,i=0){this.x=e,this.y=t,this.z=i}set(e,t,i){return i===void 0&&(i=this.z),this.x=e,this.y=t,this.z=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("THREE.Vector3: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("THREE.Vector3: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(qd.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(qd.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,i=this.y,r=this.z,a=e.elements;return this.x=a[0]*t+a[3]*i+a[6]*r,this.y=a[1]*t+a[4]*i+a[7]*r,this.z=a[2]*t+a[5]*i+a[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,i=this.y,r=this.z,a=e.elements,o=1/(a[3]*t+a[7]*i+a[11]*r+a[15]);return this.x=(a[0]*t+a[4]*i+a[8]*r+a[12])*o,this.y=(a[1]*t+a[5]*i+a[9]*r+a[13])*o,this.z=(a[2]*t+a[6]*i+a[10]*r+a[14])*o,this}applyQuaternion(e){const t=this.x,i=this.y,r=this.z,a=e.x,o=e.y,l=e.z,c=e.w,u=2*(o*r-l*i),f=2*(l*t-a*r),h=2*(a*i-o*t);return this.x=t+c*u+o*h-l*f,this.y=i+c*f+l*u-a*h,this.z=r+c*h+a*f-o*u,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,i=this.y,r=this.z,a=e.elements;return this.x=a[0]*t+a[4]*i+a[8]*r,this.y=a[1]*t+a[5]*i+a[9]*r,this.z=a[2]*t+a[6]*i+a[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=St(this.x,e.x,t.x),this.y=St(this.y,e.y,t.y),this.z=St(this.z,e.z,t.z),this}clampScalar(e,t){return this.x=St(this.x,e,t),this.y=St(this.y,e,t),this.z=St(this.z,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(St(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this.z=e.z+(t.z-e.z)*i,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const i=e.x,r=e.y,a=e.z,o=t.x,l=t.y,c=t.z;return this.x=r*c-a*l,this.y=a*o-i*c,this.z=i*l-r*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const i=e.dot(this)/t;return this.copy(e).multiplyScalar(i)}projectOnPlane(e){return $o.copy(this).projectOnVector(e),this.sub($o)}reflect(e){return this.sub($o.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const i=this.dot(e)/t;return Math.acos(St(i,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,i=this.y-e.y,r=this.z-e.z;return t*t+i*i+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,i){const r=Math.sin(t)*e;return this.x=r*Math.sin(i),this.y=Math.cos(t)*e,this.z=r*Math.cos(i),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,i){return this.x=e*Math.sin(t),this.y=i,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),i=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=i,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,i=Math.sqrt(1-t*t);return this.x=i*Math.cos(e),this.y=t,this.z=i*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}};Cu.prototype.isVector3=!0;let ge=Cu;const $o=new ge,qd=new ha,Iu=class Iu{constructor(e,t,i,r,a,o,l,c,u){this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,i,r,a,o,l,c,u)}set(e,t,i,r,a,o,l,c,u){const f=this.elements;return f[0]=e,f[1]=r,f[2]=l,f[3]=t,f[4]=a,f[5]=c,f[6]=i,f[7]=o,f[8]=u,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,i=e.elements;return t[0]=i[0],t[1]=i[1],t[2]=i[2],t[3]=i[3],t[4]=i[4],t[5]=i[5],t[6]=i[6],t[7]=i[7],t[8]=i[8],this}extractBasis(e,t,i){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),i.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const i=e.elements,r=t.elements,a=this.elements,o=i[0],l=i[3],c=i[6],u=i[1],f=i[4],h=i[7],d=i[2],p=i[5],m=i[8],E=r[0],g=r[3],_=r[6],O=r[1],D=r[4],y=r[7],B=r[2],R=r[5],C=r[8];return a[0]=o*E+l*O+c*B,a[3]=o*g+l*D+c*R,a[6]=o*_+l*y+c*C,a[1]=u*E+f*O+h*B,a[4]=u*g+f*D+h*R,a[7]=u*_+f*y+h*C,a[2]=d*E+p*O+m*B,a[5]=d*g+p*D+m*R,a[8]=d*_+p*y+m*C,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],i=e[1],r=e[2],a=e[3],o=e[4],l=e[5],c=e[6],u=e[7],f=e[8];return t*o*f-t*l*u-i*a*f+i*l*c+r*a*u-r*o*c}invert(){const e=this.elements,t=e[0],i=e[1],r=e[2],a=e[3],o=e[4],l=e[5],c=e[6],u=e[7],f=e[8],h=f*o-l*u,d=l*c-f*a,p=u*a-o*c,m=t*h+i*d+r*p;if(m===0)return this.set(0,0,0,0,0,0,0,0,0);const E=1/m;return e[0]=h*E,e[1]=(r*u-f*i)*E,e[2]=(l*i-r*o)*E,e[3]=d*E,e[4]=(f*t-r*c)*E,e[5]=(r*a-l*t)*E,e[6]=p*E,e[7]=(i*c-u*t)*E,e[8]=(o*t-i*a)*E,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,i,r,a,o,l){const c=Math.cos(a),u=Math.sin(a);return this.set(i*c,i*u,-i*(c*o+u*l)+o+e,-r*u,r*c,-r*(-u*o+c*l)+l+t,0,0,1),this}scale(e,t){return ia("Matrix3: .scale() is deprecated. Use .makeScale() instead."),this.premultiply(Xo.makeScale(e,t)),this}rotate(e){return ia("Matrix3: .rotate() is deprecated. Use .makeRotation() instead."),this.premultiply(Xo.makeRotation(-e)),this}translate(e,t){return ia("Matrix3: .translate() is deprecated. Use .makeTranslation() instead."),this.premultiply(Xo.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,-i,0,i,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,i=e.elements;for(let r=0;r<9;r++)if(t[r]!==i[r])return!1;return!0}fromArray(e,t=0){for(let i=0;i<9;i++)this.elements[i]=e[i+t];return this}toArray(e=[],t=0){const i=this.elements;return e[t]=i[0],e[t+1]=i[1],e[t+2]=i[2],e[t+3]=i[3],e[t+4]=i[4],e[t+5]=i[5],e[t+6]=i[6],e[t+7]=i[7],e[t+8]=i[8],e}clone(){return new this.constructor().fromArray(this.elements)}};Iu.prototype.isMatrix3=!0;let ht=Iu;const Xo=new ht,Yd=new ht().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Kd=new ht().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function DE(){const n={enabled:!0,workingColorSpace:oo,spaces:{},convert:function(r,a,o){return this.enabled===!1||a===o||!a||!o||(this.spaces[a].transfer===Nt&&(r.r=Ci(r.r),r.g=Ci(r.g),r.b=Ci(r.b)),this.spaces[a].primaries!==this.spaces[o].primaries&&(r.applyMatrix3(this.spaces[a].toXYZ),r.applyMatrix3(this.spaces[o].fromXYZ)),this.spaces[o].transfer===Nt&&(r.r=ra(r.r),r.g=ra(r.g),r.b=ra(r.b))),r},workingToColorSpace:function(r,a){return this.convert(r,this.workingColorSpace,a)},colorSpaceToWorking:function(r,a){return this.convert(r,a,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===Ji?lo:this.spaces[r].transfer},getToneMappingMode:function(r){return this.spaces[r].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(r,a=this.workingColorSpace){return r.fromArray(this.spaces[a].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,a,o){return r.copy(this.spaces[a].toXYZ).multiply(this.spaces[o].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(r,a){return ia("ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),n.workingToColorSpace(r,a)},toWorkingColorSpace:function(r,a){return ia("ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),n.colorSpaceToWorking(r,a)}},e=[.64,.33,.3,.6,.15,.06],t=[.2126,.7152,.0722],i=[.3127,.329];return n.define({[oo]:{primaries:e,whitePoint:i,transfer:lo,toXYZ:Yd,fromXYZ:Kd,luminanceCoefficients:t,workingColorSpaceConfig:{unpackColorSpace:Rn},outputColorSpaceConfig:{drawingBufferColorSpace:Rn}},[Rn]:{primaries:e,whitePoint:i,transfer:Nt,toXYZ:Yd,fromXYZ:Kd,luminanceCoefficients:t,outputColorSpaceConfig:{drawingBufferColorSpace:Rn}}}),n}const bt=DE();function Ci(n){return n<.04045?n*.0773993808:Math.pow(n*.9478672986+.0521327014,2.4)}function ra(n){return n<.0031308?n*12.92:1.055*Math.pow(n,.41666)-.055}let Fr;class kE{static getDataURL(e,t="image/png"){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let i;if(e instanceof HTMLCanvasElement)i=e;else{Fr===void 0&&(Fr=co("canvas")),Fr.width=e.width,Fr.height=e.height;const r=Fr.getContext("2d");e instanceof ImageData?r.putImageData(e,0,0):r.drawImage(e,0,0,e.width,e.height),i=Fr}return i.toDataURL(t)}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=co("canvas");t.width=e.width,t.height=e.height;const i=t.getContext("2d");i.drawImage(e,0,0,e.width,e.height);const r=i.getImageData(0,0,e.width,e.height),a=r.data;for(let o=0;o<a.length;o++)a[o]=Ci(a[o]/255)*255;return i.putImageData(r,0,0),t}else if(e.data){const t=e.data.slice(0);for(let i=0;i<t.length;i++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[i]=Math.floor(Ci(t[i]/255)*255):t[i]=Ci(t[i]);return{data:t,width:e.width,height:e.height}}else return ut("ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let UE=0;class yu{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:UE++}),this.uuid=as(),this.data=e,this.dataReady=!0,this.version=0}getSize(e){const t=this.data;return typeof HTMLVideoElement<"u"&&t instanceof HTMLVideoElement?e.set(t.videoWidth,t.videoHeight,0):typeof VideoFrame<"u"&&t instanceof VideoFrame?e.set(t.displayWidth,t.displayHeight,0):t!==null?e.set(t.width,t.height,t.depth||0):e.set(0,0,0),e}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const i={uuid:this.uuid,url:""},r=this.data;if(r!==null){let a;if(Array.isArray(r)){a=[];for(let o=0,l=r.length;o<l;o++)r[o].isDataTexture?a.push(qo(r[o].image)):a.push(qo(r[o]))}else a=qo(r);i.url=a}return t||(e.images[this.uuid]=i),i}}function qo(n){return typeof HTMLImageElement<"u"&&n instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&n instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&n instanceof ImageBitmap?kE.getDataURL(n):n.data?{data:Array.from(n.data),width:n.width,height:n.height,type:n.data.constructor.name}:(ut("Texture: Unable to serialize Texture."),{})}let OE=0;const Yo=new ge;class _n extends Ar{constructor(e=_n.DEFAULT_IMAGE,t=_n.DEFAULT_MAPPING,i=wi,r=wi,a=fn,o=pr,l=Xn,c=In,u=_n.DEFAULT_ANISOTROPY,f=Ji){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:OE++}),this.uuid=as(),this.name="",this.source=new yu(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=i,this.wrapT=r,this.magFilter=a,this.minFilter=o,this.anisotropy=u,this.format=l,this.internalFormat=null,this.type=c,this.offset=new xt(0,0),this.repeat=new xt(1,1),this.center=new xt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ht,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(e&&e.depth&&e.depth>1),this.pmremVersion=0,this.normalized=!1}get width(){return this.source.getSize(Yo).x}get height(){return this.source.getSize(Yo).y}get depth(){return this.source.getSize(Yo).z}get image(){return this.source.data}set image(e){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.normalized=e.normalized,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.renderTarget=e.renderTarget,this.isRenderTargetTexture=e.isRenderTargetTexture,this.isArrayTexture=e.isArrayTexture,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}setValues(e){for(const t in e){const i=e[t];if(i===void 0){ut(`Texture.setValues(): parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){ut(`Texture.setValues(): property '${t}' does not exist.`);continue}r&&i&&r.isVector2&&i.isVector2||r&&i&&r.isVector3&&i.isVector3||r&&i&&r.isMatrix3&&i.isMatrix3?r.copy(i):this[t]=i}}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const i={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,normalized:this.normalized,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(i.userData=this.userData),t||(e.textures[this.uuid]=i),i}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==xp)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Hl:e.x=e.x-Math.floor(e.x);break;case wi:e.x=e.x<0?0:1;break;case Gl:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Hl:e.y=e.y-Math.floor(e.y);break;case wi:e.y=e.y<0?0:1;break;case Gl:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}_n.DEFAULT_IMAGE=null;_n.DEFAULT_MAPPING=xp;_n.DEFAULT_ANISOTROPY=1;const Nu=class Nu{constructor(e=0,t=0,i=0,r=1){this.x=e,this.y=t,this.z=i,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,i,r){return this.x=e,this.y=t,this.z=i,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("THREE.Vector4: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("THREE.Vector4: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,i=this.y,r=this.z,a=this.w,o=e.elements;return this.x=o[0]*t+o[4]*i+o[8]*r+o[12]*a,this.y=o[1]*t+o[5]*i+o[9]*r+o[13]*a,this.z=o[2]*t+o[6]*i+o[10]*r+o[14]*a,this.w=o[3]*t+o[7]*i+o[11]*r+o[15]*a,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,i,r,a;const c=e.elements,u=c[0],f=c[4],h=c[8],d=c[1],p=c[5],m=c[9],E=c[2],g=c[6],_=c[10];if(Math.abs(f-d)<.01&&Math.abs(h-E)<.01&&Math.abs(m-g)<.01){if(Math.abs(f+d)<.1&&Math.abs(h+E)<.1&&Math.abs(m+g)<.1&&Math.abs(u+p+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const D=(u+1)/2,y=(p+1)/2,B=(_+1)/2,R=(f+d)/4,C=(h+E)/4,b=(m+g)/4;return D>y&&D>B?D<.01?(i=0,r=.707106781,a=.707106781):(i=Math.sqrt(D),r=R/i,a=C/i):y>B?y<.01?(i=.707106781,r=0,a=.707106781):(r=Math.sqrt(y),i=R/r,a=b/r):B<.01?(i=.707106781,r=.707106781,a=0):(a=Math.sqrt(B),i=C/a,r=b/a),this.set(i,r,a,t),this}let O=Math.sqrt((g-m)*(g-m)+(h-E)*(h-E)+(d-f)*(d-f));return Math.abs(O)<.001&&(O=1),this.x=(g-m)/O,this.y=(h-E)/O,this.z=(d-f)/O,this.w=Math.acos((u+p+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=St(this.x,e.x,t.x),this.y=St(this.y,e.y,t.y),this.z=St(this.z,e.z,t.z),this.w=St(this.w,e.w,t.w),this}clampScalar(e,t){return this.x=St(this.x,e,t),this.y=St(this.y,e,t),this.z=St(this.z,e,t),this.w=St(this.w,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(St(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this.z=e.z+(t.z-e.z)*i,this.w=e.w+(t.w-e.w)*i,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}};Nu.prototype.isVector4=!0;let Gt=Nu;class FE extends Ar{constructor(e=1,t=1,i={}){super(),i=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:fn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1,useArrayDepthTexture:!1},i),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=i.depth,this.scissor=new Gt(0,0,e,t),this.scissorTest=!1,this.viewport=new Gt(0,0,e,t),this.textures=[];const r={width:e,height:t,depth:i.depth},a=new _n(r),o=i.count;for(let l=0;l<o;l++)this.textures[l]=a.clone(),this.textures[l].isRenderTargetTexture=!0,this.textures[l].renderTarget=this;this._setTextureOptions(i),this.depthBuffer=i.depthBuffer,this.stencilBuffer=i.stencilBuffer,this.resolveDepthBuffer=i.resolveDepthBuffer,this.resolveStencilBuffer=i.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=i.depthTexture,this.samples=i.samples,this.multiview=i.multiview,this.useArrayDepthTexture=i.useArrayDepthTexture}_setTextureOptions(e={}){const t={minFilter:fn,generateMipmaps:!1,flipY:!1,internalFormat:null};e.mapping!==void 0&&(t.mapping=e.mapping),e.wrapS!==void 0&&(t.wrapS=e.wrapS),e.wrapT!==void 0&&(t.wrapT=e.wrapT),e.wrapR!==void 0&&(t.wrapR=e.wrapR),e.magFilter!==void 0&&(t.magFilter=e.magFilter),e.minFilter!==void 0&&(t.minFilter=e.minFilter),e.format!==void 0&&(t.format=e.format),e.type!==void 0&&(t.type=e.type),e.anisotropy!==void 0&&(t.anisotropy=e.anisotropy),e.colorSpace!==void 0&&(t.colorSpace=e.colorSpace),e.flipY!==void 0&&(t.flipY=e.flipY),e.generateMipmaps!==void 0&&(t.generateMipmaps=e.generateMipmaps),e.internalFormat!==void 0&&(t.internalFormat=e.internalFormat);for(let i=0;i<this.textures.length;i++)this.textures[i].setValues(t)}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}set depthTexture(e){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),e!==null&&(e.renderTarget=this),this._depthTexture=e}get depthTexture(){return this._depthTexture}setSize(e,t,i=1){if(this.width!==e||this.height!==t||this.depth!==i){this.width=e,this.height=t,this.depth=i;for(let r=0,a=this.textures.length;r<a;r++)this.textures[r].image.width=e,this.textures[r].image.height=t,this.textures[r].image.depth=i,this.textures[r].isData3DTexture!==!0&&(this.textures[r].isArrayTexture=this.textures[r].image.depth>1);this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let t=0,i=e.textures.length;t<i;t++){this.textures[t]=e.textures[t].clone(),this.textures[t].isRenderTargetTexture=!0,this.textures[t].renderTarget=this;const r=Object.assign({},e.textures[t].image);this.textures[t].source=new yu(r)}return this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this.multiview=e.multiview,this.useArrayDepthTexture=e.useArrayDepthTexture,this}dispose(){this.dispatchEvent({type:"dispose"})}}class fi extends FE{constructor(e=1,t=1,i={}){super(e,t,i),this.isWebGLRenderTarget=!0}}class Rp extends _n{constructor(e=null,t=1,i=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:i,depth:r},this.magFilter=an,this.minFilter=an,this.wrapR=wi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class BE extends _n{constructor(e=null,t=1,i=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:i,depth:r},this.magFilter=an,this.minFilter=an,this.wrapR=wi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const uo=class uo{constructor(e,t,i,r,a,o,l,c,u,f,h,d,p,m,E,g){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,i,r,a,o,l,c,u,f,h,d,p,m,E,g)}set(e,t,i,r,a,o,l,c,u,f,h,d,p,m,E,g){const _=this.elements;return _[0]=e,_[4]=t,_[8]=i,_[12]=r,_[1]=a,_[5]=o,_[9]=l,_[13]=c,_[2]=u,_[6]=f,_[10]=h,_[14]=d,_[3]=p,_[7]=m,_[11]=E,_[15]=g,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new uo().fromArray(this.elements)}copy(e){const t=this.elements,i=e.elements;return t[0]=i[0],t[1]=i[1],t[2]=i[2],t[3]=i[3],t[4]=i[4],t[5]=i[5],t[6]=i[6],t[7]=i[7],t[8]=i[8],t[9]=i[9],t[10]=i[10],t[11]=i[11],t[12]=i[12],t[13]=i[13],t[14]=i[14],t[15]=i[15],this}copyPosition(e){const t=this.elements,i=e.elements;return t[12]=i[12],t[13]=i[13],t[14]=i[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,i){return this.determinantAffine()===0?(e.set(1,0,0),t.set(0,1,0),i.set(0,0,1),this):(e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),i.setFromMatrixColumn(this,2),this)}makeBasis(e,t,i){return this.set(e.x,t.x,i.x,0,e.y,t.y,i.y,0,e.z,t.z,i.z,0,0,0,0,1),this}extractRotation(e){if(e.determinantAffine()===0)return this.identity();const t=this.elements,i=e.elements,r=1/Br.setFromMatrixColumn(e,0).length(),a=1/Br.setFromMatrixColumn(e,1).length(),o=1/Br.setFromMatrixColumn(e,2).length();return t[0]=i[0]*r,t[1]=i[1]*r,t[2]=i[2]*r,t[3]=0,t[4]=i[4]*a,t[5]=i[5]*a,t[6]=i[6]*a,t[7]=0,t[8]=i[8]*o,t[9]=i[9]*o,t[10]=i[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,i=e.x,r=e.y,a=e.z,o=Math.cos(i),l=Math.sin(i),c=Math.cos(r),u=Math.sin(r),f=Math.cos(a),h=Math.sin(a);if(e.order==="XYZ"){const d=o*f,p=o*h,m=l*f,E=l*h;t[0]=c*f,t[4]=-c*h,t[8]=u,t[1]=p+m*u,t[5]=d-E*u,t[9]=-l*c,t[2]=E-d*u,t[6]=m+p*u,t[10]=o*c}else if(e.order==="YXZ"){const d=c*f,p=c*h,m=u*f,E=u*h;t[0]=d+E*l,t[4]=m*l-p,t[8]=o*u,t[1]=o*h,t[5]=o*f,t[9]=-l,t[2]=p*l-m,t[6]=E+d*l,t[10]=o*c}else if(e.order==="ZXY"){const d=c*f,p=c*h,m=u*f,E=u*h;t[0]=d-E*l,t[4]=-o*h,t[8]=m+p*l,t[1]=p+m*l,t[5]=o*f,t[9]=E-d*l,t[2]=-o*u,t[6]=l,t[10]=o*c}else if(e.order==="ZYX"){const d=o*f,p=o*h,m=l*f,E=l*h;t[0]=c*f,t[4]=m*u-p,t[8]=d*u+E,t[1]=c*h,t[5]=E*u+d,t[9]=p*u-m,t[2]=-u,t[6]=l*c,t[10]=o*c}else if(e.order==="YZX"){const d=o*c,p=o*u,m=l*c,E=l*u;t[0]=c*f,t[4]=E-d*h,t[8]=m*h+p,t[1]=h,t[5]=o*f,t[9]=-l*f,t[2]=-u*f,t[6]=p*h+m,t[10]=d-E*h}else if(e.order==="XZY"){const d=o*c,p=o*u,m=l*c,E=l*u;t[0]=c*f,t[4]=-h,t[8]=u*f,t[1]=d*h+E,t[5]=o*f,t[9]=p*h-m,t[2]=m*h-p,t[6]=l*f,t[10]=E*h+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(zE,e,HE)}lookAt(e,t,i){const r=this.elements;return wn.subVectors(e,t),wn.lengthSq()===0&&(wn.z=1),wn.normalize(),$i.crossVectors(i,wn),$i.lengthSq()===0&&(Math.abs(i.z)===1?wn.x+=1e-4:wn.z+=1e-4,wn.normalize(),$i.crossVectors(i,wn)),$i.normalize(),bs.crossVectors(wn,$i),r[0]=$i.x,r[4]=bs.x,r[8]=wn.x,r[1]=$i.y,r[5]=bs.y,r[9]=wn.y,r[2]=$i.z,r[6]=bs.z,r[10]=wn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const i=e.elements,r=t.elements,a=this.elements,o=i[0],l=i[4],c=i[8],u=i[12],f=i[1],h=i[5],d=i[9],p=i[13],m=i[2],E=i[6],g=i[10],_=i[14],O=i[3],D=i[7],y=i[11],B=i[15],R=r[0],C=r[4],b=r[8],A=r[12],k=r[1],z=r[5],H=r[9],q=r[13],Q=r[2],G=r[6],T=r[10],w=r[14],I=r[3],F=r[7],Y=r[11],te=r[15];return a[0]=o*R+l*k+c*Q+u*I,a[4]=o*C+l*z+c*G+u*F,a[8]=o*b+l*H+c*T+u*Y,a[12]=o*A+l*q+c*w+u*te,a[1]=f*R+h*k+d*Q+p*I,a[5]=f*C+h*z+d*G+p*F,a[9]=f*b+h*H+d*T+p*Y,a[13]=f*A+h*q+d*w+p*te,a[2]=m*R+E*k+g*Q+_*I,a[6]=m*C+E*z+g*G+_*F,a[10]=m*b+E*H+g*T+_*Y,a[14]=m*A+E*q+g*w+_*te,a[3]=O*R+D*k+y*Q+B*I,a[7]=O*C+D*z+y*G+B*F,a[11]=O*b+D*H+y*T+B*Y,a[15]=O*A+D*q+y*w+B*te,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],i=e[4],r=e[8],a=e[12],o=e[1],l=e[5],c=e[9],u=e[13],f=e[2],h=e[6],d=e[10],p=e[14],m=e[3],E=e[7],g=e[11],_=e[15],O=c*p-u*d,D=l*p-u*h,y=l*d-c*h,B=o*p-u*f,R=o*d-c*f,C=o*h-l*f;return t*(E*O-g*D+_*y)-i*(m*O-g*B+_*R)+r*(m*D-E*B+_*C)-a*(m*y-E*R+g*C)}determinantAffine(){const e=this.elements,t=e[0],i=e[4],r=e[8],a=e[1],o=e[5],l=e[9],c=e[2],u=e[6],f=e[10];return t*(o*f-l*u)-i*(a*f-l*c)+r*(a*u-o*c)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,i){const r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=i),this}invert(){const e=this.elements,t=e[0],i=e[1],r=e[2],a=e[3],o=e[4],l=e[5],c=e[6],u=e[7],f=e[8],h=e[9],d=e[10],p=e[11],m=e[12],E=e[13],g=e[14],_=e[15],O=t*l-i*o,D=t*c-r*o,y=t*u-a*o,B=i*c-r*l,R=i*u-a*l,C=r*u-a*c,b=f*E-h*m,A=f*g-d*m,k=f*_-p*m,z=h*g-d*E,H=h*_-p*E,q=d*_-p*g,Q=O*q-D*H+y*z+B*k-R*A+C*b;if(Q===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const G=1/Q;return e[0]=(l*q-c*H+u*z)*G,e[1]=(r*H-i*q-a*z)*G,e[2]=(E*C-g*R+_*B)*G,e[3]=(d*R-h*C-p*B)*G,e[4]=(c*k-o*q-u*A)*G,e[5]=(t*q-r*k+a*A)*G,e[6]=(g*y-m*C-_*D)*G,e[7]=(f*C-d*y+p*D)*G,e[8]=(o*H-l*k+u*b)*G,e[9]=(i*k-t*H-a*b)*G,e[10]=(m*R-E*y+_*O)*G,e[11]=(h*y-f*R-p*O)*G,e[12]=(l*A-o*z-c*b)*G,e[13]=(t*z-i*A+r*b)*G,e[14]=(E*D-m*B-g*O)*G,e[15]=(f*B-h*D+d*O)*G,this}scale(e){const t=this.elements,i=e.x,r=e.y,a=e.z;return t[0]*=i,t[4]*=r,t[8]*=a,t[1]*=i,t[5]*=r,t[9]*=a,t[2]*=i,t[6]*=r,t[10]*=a,t[3]*=i,t[7]*=r,t[11]*=a,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],i=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,i,r))}makeTranslation(e,t,i){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,i,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),i=Math.sin(e);return this.set(1,0,0,0,0,t,-i,0,0,i,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,0,i,0,0,1,0,0,-i,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,-i,0,0,i,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const i=Math.cos(t),r=Math.sin(t),a=1-i,o=e.x,l=e.y,c=e.z,u=a*o,f=a*l;return this.set(u*o+i,u*l-r*c,u*c+r*l,0,u*l+r*c,f*l+i,f*c-r*o,0,u*c-r*l,f*c+r*o,a*c*c+i,0,0,0,0,1),this}makeScale(e,t,i){return this.set(e,0,0,0,0,t,0,0,0,0,i,0,0,0,0,1),this}makeShear(e,t,i,r,a,o){return this.set(1,i,a,0,e,1,o,0,t,r,1,0,0,0,0,1),this}compose(e,t,i){const r=this.elements,a=t._x,o=t._y,l=t._z,c=t._w,u=a+a,f=o+o,h=l+l,d=a*u,p=a*f,m=a*h,E=o*f,g=o*h,_=l*h,O=c*u,D=c*f,y=c*h,B=i.x,R=i.y,C=i.z;return r[0]=(1-(E+_))*B,r[1]=(p+y)*B,r[2]=(m-D)*B,r[3]=0,r[4]=(p-y)*R,r[5]=(1-(d+_))*R,r[6]=(g+O)*R,r[7]=0,r[8]=(m+D)*C,r[9]=(g-O)*C,r[10]=(1-(d+E))*C,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,i){const r=this.elements;e.x=r[12],e.y=r[13],e.z=r[14];const a=this.determinantAffine();if(a===0)return i.set(1,1,1),t.identity(),this;let o=Br.set(r[0],r[1],r[2]).length();const l=Br.set(r[4],r[5],r[6]).length(),c=Br.set(r[8],r[9],r[10]).length();a<0&&(o=-o),Fn.copy(this);const u=1/o,f=1/l,h=1/c;return Fn.elements[0]*=u,Fn.elements[1]*=u,Fn.elements[2]*=u,Fn.elements[4]*=f,Fn.elements[5]*=f,Fn.elements[6]*=f,Fn.elements[8]*=h,Fn.elements[9]*=h,Fn.elements[10]*=h,t.setFromRotationMatrix(Fn),i.x=o,i.y=l,i.z=c,this}makePerspective(e,t,i,r,a,o,l=ui,c=!1){const u=this.elements,f=2*a/(t-e),h=2*a/(i-r),d=(t+e)/(t-e),p=(i+r)/(i-r);let m,E;if(c)m=a/(o-a),E=o*a/(o-a);else if(l===ui)m=-(o+a)/(o-a),E=-2*o*a/(o-a);else if(l===Qa)m=-o/(o-a),E=-o*a/(o-a);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+l);return u[0]=f,u[4]=0,u[8]=d,u[12]=0,u[1]=0,u[5]=h,u[9]=p,u[13]=0,u[2]=0,u[6]=0,u[10]=m,u[14]=E,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,i,r,a,o,l=ui,c=!1){const u=this.elements,f=2/(t-e),h=2/(i-r),d=-(t+e)/(t-e),p=-(i+r)/(i-r);let m,E;if(c)m=1/(o-a),E=o/(o-a);else if(l===ui)m=-2/(o-a),E=-(o+a)/(o-a);else if(l===Qa)m=-1/(o-a),E=-a/(o-a);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+l);return u[0]=f,u[4]=0,u[8]=0,u[12]=d,u[1]=0,u[5]=h,u[9]=0,u[13]=p,u[2]=0,u[6]=0,u[10]=m,u[14]=E,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,i=e.elements;for(let r=0;r<16;r++)if(t[r]!==i[r])return!1;return!0}fromArray(e,t=0){for(let i=0;i<16;i++)this.elements[i]=e[i+t];return this}toArray(e=[],t=0){const i=this.elements;return e[t]=i[0],e[t+1]=i[1],e[t+2]=i[2],e[t+3]=i[3],e[t+4]=i[4],e[t+5]=i[5],e[t+6]=i[6],e[t+7]=i[7],e[t+8]=i[8],e[t+9]=i[9],e[t+10]=i[10],e[t+11]=i[11],e[t+12]=i[12],e[t+13]=i[13],e[t+14]=i[14],e[t+15]=i[15],e}};uo.prototype.isMatrix4=!0;let Xt=uo;const Br=new ge,Fn=new Xt,zE=new ge(0,0,0),HE=new ge(1,1,1),$i=new ge,bs=new ge,wn=new ge,Zd=new Xt,Jd=new ha;class yr{constructor(e=0,t=0,i=0,r=yr.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=i,this._order=r}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,i,r=this._order){return this._x=e,this._y=t,this._z=i,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,i=!0){const r=e.elements,a=r[0],o=r[4],l=r[8],c=r[1],u=r[5],f=r[9],h=r[2],d=r[6],p=r[10];switch(t){case"XYZ":this._y=Math.asin(St(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-f,p),this._z=Math.atan2(-o,a)):(this._x=Math.atan2(d,u),this._z=0);break;case"YXZ":this._x=Math.asin(-St(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(l,p),this._z=Math.atan2(c,u)):(this._y=Math.atan2(-h,a),this._z=0);break;case"ZXY":this._x=Math.asin(St(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-h,p),this._z=Math.atan2(-o,u)):(this._y=0,this._z=Math.atan2(c,a));break;case"ZYX":this._y=Math.asin(-St(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(d,p),this._z=Math.atan2(c,a)):(this._x=0,this._z=Math.atan2(-o,u));break;case"YZX":this._z=Math.asin(St(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,u),this._y=Math.atan2(-h,a)):(this._x=0,this._y=Math.atan2(l,p));break;case"XZY":this._z=Math.asin(-St(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(d,u),this._y=Math.atan2(l,a)):(this._x=Math.atan2(-f,p),this._y=0);break;default:ut("Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,i===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,i){return Zd.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Zd,t,i)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Jd.setFromEuler(this),this.setFromQuaternion(Jd,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}yr.DEFAULT_ORDER="XYZ";class Cp{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let GE=0;const Qd=new ge,zr=new ha,bi=new Xt,Ss=new ge,wa=new ge,VE=new ge,WE=new ha,jd=new ge(1,0,0),ef=new ge(0,1,0),tf=new ge(0,0,1),nf={type:"added"},$E={type:"removed"},Hr={type:"childadded",child:null},Ko={type:"childremoved",child:null};class En extends Ar{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:GE++}),this.uuid=as(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=En.DEFAULT_UP.clone();const e=new ge,t=new yr,i=new ha,r=new ge(1,1,1);function a(){i.setFromEuler(t,!1)}function o(){t.setFromQuaternion(i,void 0,!1)}t._onChange(a),i._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:i},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new Xt},normalMatrix:{value:new ht}}),this.matrix=new Xt,this.matrixWorld=new Xt,this.matrixAutoUpdate=En.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=En.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Cp,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return zr.setFromAxisAngle(e,t),this.quaternion.multiply(zr),this}rotateOnWorldAxis(e,t){return zr.setFromAxisAngle(e,t),this.quaternion.premultiply(zr),this}rotateX(e){return this.rotateOnAxis(jd,e)}rotateY(e){return this.rotateOnAxis(ef,e)}rotateZ(e){return this.rotateOnAxis(tf,e)}translateOnAxis(e,t){return Qd.copy(e).applyQuaternion(this.quaternion),this.position.add(Qd.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(jd,e)}translateY(e){return this.translateOnAxis(ef,e)}translateZ(e){return this.translateOnAxis(tf,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(bi.copy(this.matrixWorld).invert())}lookAt(e,t,i){e.isVector3?Ss.copy(e):Ss.set(e,t,i);const r=this.parent;this.updateWorldMatrix(!0,!1),wa.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?bi.lookAt(wa,Ss,this.up):bi.lookAt(Ss,wa,this.up),this.quaternion.setFromRotationMatrix(bi),r&&(bi.extractRotation(r.matrixWorld),zr.setFromRotationMatrix(bi),this.quaternion.premultiply(zr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(Rt("Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(nf),Hr.child=e,this.dispatchEvent(Hr),Hr.child=null):Rt("Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let i=0;i<arguments.length;i++)this.remove(arguments[i]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent($E),Ko.child=e,this.dispatchEvent(Ko),Ko.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),bi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),bi.multiply(e.parent.matrixWorld)),e.applyMatrix4(bi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(nf),Hr.child=e,this.dispatchEvent(Hr),Hr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let i=0,r=this.children.length;i<r;i++){const o=this.children[i].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,i=[]){this[e]===t&&i.push(this);const r=this.children;for(let a=0,o=r.length;a<o;a++)r[a].getObjectsByProperty(e,t,i);return i}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(wa,e,VE),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(wa,WE,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);const e=this.pivot;if(e!==null){const t=e.x,i=e.y,r=e.z,a=this.matrix.elements;a[12]+=t-a[0]*t-a[4]*i-a[8]*r,a[13]+=i-a[1]*t-a[5]*i-a[9]*r,a[14]+=r-a[2]*t-a[6]*i-a[10]*r}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].updateMatrixWorld(e)}updateWorldMatrix(e,t,i=!1){const r=this.parent;if(e===!0&&r!==null&&r.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||i)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,i=!0),t===!0){const a=this.children;for(let o=0,l=a.length;o<l;o++)a[o].updateWorldMatrix(!1,!0,i)}}toJSON(e){const t=e===void 0||typeof e=="string",i={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},i.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),this.static!==!1&&(r.static=this.static),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.pivot!==null&&(r.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(r.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(r.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.geometryInfo=this._geometryInfo.map(l=>({...l,boundingBox:l.boundingBox?l.boundingBox.toJSON():void 0,boundingSphere:l.boundingSphere?l.boundingSphere.toJSON():void 0})),r.instanceInfo=this._instanceInfo.map(l=>({...l})),r.availableInstanceIds=this._availableInstanceIds.slice(),r.availableGeometryIds=this._availableGeometryIds.slice(),r.nextIndexStart=this._nextIndexStart,r.nextVertexStart=this._nextVertexStart,r.geometryCount=this._geometryCount,r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.matricesTexture=this._matricesTexture.toJSON(e),r.indirectTexture=this._indirectTexture.toJSON(e),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(r.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(r.boundingBox=this.boundingBox.toJSON()));function a(l,c){return l[c.uuid]===void 0&&(l[c.uuid]=c.toJSON(e)),c.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=a(e.geometries,this.geometry);const l=this.geometry.parameters;if(l!==void 0&&l.shapes!==void 0){const c=l.shapes;if(Array.isArray(c))for(let u=0,f=c.length;u<f;u++){const h=c[u];a(e.shapes,h)}else a(e.shapes,c)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(a(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const l=[];for(let c=0,u=this.material.length;c<u;c++)l.push(a(e.materials,this.material[c]));r.material=l}else r.material=a(e.materials,this.material);if(this.children.length>0){r.children=[];for(let l=0;l<this.children.length;l++)r.children.push(this.children[l].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let l=0;l<this.animations.length;l++){const c=this.animations[l];r.animations.push(a(e.animations,c))}}if(t){const l=o(e.geometries),c=o(e.materials),u=o(e.textures),f=o(e.images),h=o(e.shapes),d=o(e.skeletons),p=o(e.animations),m=o(e.nodes);l.length>0&&(i.geometries=l),c.length>0&&(i.materials=c),u.length>0&&(i.textures=u),f.length>0&&(i.images=f),h.length>0&&(i.shapes=h),d.length>0&&(i.skeletons=d),p.length>0&&(i.animations=p),m.length>0&&(i.nodes=m)}return i.object=r,i;function o(l){const c=[];for(const u in l){const f=l[u];delete f.metadata,c.push(f)}return c}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.pivot=e.pivot!==null?e.pivot.clone():null,this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.static=e.static,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let i=0;i<e.children.length;i++){const r=e.children[i];this.add(r.clone())}return this}}En.DEFAULT_UP=new ge(0,1,0);En.DEFAULT_MATRIX_AUTO_UPDATE=!0;En.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;class ys extends En{constructor(){super(),this.isGroup=!0,this.type="Group"}}const XE={type:"move"};class Zo{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new ys,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new ys,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new ge,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new ge),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new ys,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new ge,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new ge,this._grip.eventsEnabled=!1),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const i of e.hand.values())this._getHandJoint(t,i)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,i){let r=null,a=null,o=null;const l=this._targetRay,c=this._grip,u=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(u&&e.hand){o=!0;for(const E of e.hand.values()){const g=t.getJointPose(E,i),_=this._getHandJoint(u,E);g!==null&&(_.matrix.fromArray(g.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=g.radius),_.visible=g!==null}const f=u.joints["index-finger-tip"],h=u.joints["thumb-tip"],d=f.position.distanceTo(h.position),p=.02,m=.005;u.inputState.pinching&&d>p+m?(u.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!u.inputState.pinching&&d<=p-m&&(u.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else c!==null&&e.gripSpace&&(a=t.getPose(e.gripSpace,i),a!==null&&(c.matrix.fromArray(a.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,a.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(a.linearVelocity)):c.hasLinearVelocity=!1,a.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(a.angularVelocity)):c.hasAngularVelocity=!1,c.eventsEnabled&&c.dispatchEvent({type:"gripUpdated",data:e,target:this})));l!==null&&(r=t.getPose(e.targetRaySpace,i),r===null&&a!==null&&(r=a),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1,this.dispatchEvent(XE)))}return l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),u!==null&&(u.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const i=new ys;i.matrixAutoUpdate=!1,i.visible=!1,e.joints[t.jointName]=i,e.add(i)}return e.joints[t.jointName]}}const Ip={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Xi={h:0,s:0,l:0},Es={h:0,s:0,l:0};function Jo(n,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?n+(e-n)*6*t:t<1/2?e:t<2/3?n+(e-n)*6*(2/3-t):n}class Ct{constructor(e,t,i){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,i)}set(e,t,i){if(t===void 0&&i===void 0){const r=e;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(e,t,i);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Rn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,bt.colorSpaceToWorking(this,t),this}setRGB(e,t,i,r=bt.workingColorSpace){return this.r=e,this.g=t,this.b=i,bt.colorSpaceToWorking(this,r),this}setHSL(e,t,i,r=bt.workingColorSpace){if(e=LE(e,1),t=St(t,0,1),i=St(i,0,1),t===0)this.r=this.g=this.b=i;else{const a=i<=.5?i*(1+t):i+t-i*t,o=2*i-a;this.r=Jo(o,a,e+1/3),this.g=Jo(o,a,e),this.b=Jo(o,a,e-1/3)}return bt.colorSpaceToWorking(this,r),this}setStyle(e,t=Rn){function i(a){a!==void 0&&parseFloat(a)<1&&ut("Color: Alpha component of "+e+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let a;const o=r[1],l=r[2];switch(o){case"rgb":case"rgba":if(a=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return i(a[4]),this.setRGB(Math.min(255,parseInt(a[1],10))/255,Math.min(255,parseInt(a[2],10))/255,Math.min(255,parseInt(a[3],10))/255,t);if(a=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return i(a[4]),this.setRGB(Math.min(100,parseInt(a[1],10))/100,Math.min(100,parseInt(a[2],10))/100,Math.min(100,parseInt(a[3],10))/100,t);break;case"hsl":case"hsla":if(a=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return i(a[4]),this.setHSL(parseFloat(a[1])/360,parseFloat(a[2])/100,parseFloat(a[3])/100,t);break;default:ut("Color: Unknown color model "+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){const a=r[1],o=a.length;if(o===3)return this.setRGB(parseInt(a.charAt(0),16)/15,parseInt(a.charAt(1),16)/15,parseInt(a.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(a,16),t);ut("Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Rn){const i=Ip[e.toLowerCase()];return i!==void 0?this.setHex(i,t):ut("Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ci(e.r),this.g=Ci(e.g),this.b=Ci(e.b),this}copyLinearToSRGB(e){return this.r=ra(e.r),this.g=ra(e.g),this.b=ra(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Rn){return bt.workingToColorSpace(ln.copy(this),e),Math.round(St(ln.r*255,0,255))*65536+Math.round(St(ln.g*255,0,255))*256+Math.round(St(ln.b*255,0,255))}getHexString(e=Rn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=bt.workingColorSpace){bt.workingToColorSpace(ln.copy(this),t);const i=ln.r,r=ln.g,a=ln.b,o=Math.max(i,r,a),l=Math.min(i,r,a);let c,u;const f=(l+o)/2;if(l===o)c=0,u=0;else{const h=o-l;switch(u=f<=.5?h/(o+l):h/(2-o-l),o){case i:c=(r-a)/h+(r<a?6:0);break;case r:c=(a-i)/h+2;break;case a:c=(i-r)/h+4;break}c/=6}return e.h=c,e.s=u,e.l=f,e}getRGB(e,t=bt.workingColorSpace){return bt.workingToColorSpace(ln.copy(this),t),e.r=ln.r,e.g=ln.g,e.b=ln.b,e}getStyle(e=Rn){bt.workingToColorSpace(ln.copy(this),e);const t=ln.r,i=ln.g,r=ln.b;return e!==Rn?`color(${e} ${t.toFixed(3)} ${i.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(i*255)},${Math.round(r*255)})`}offsetHSL(e,t,i){return this.getHSL(Xi),this.setHSL(Xi.h+e,Xi.s+t,Xi.l+i)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,i){return this.r=e.r+(t.r-e.r)*i,this.g=e.g+(t.g-e.g)*i,this.b=e.b+(t.b-e.b)*i,this}lerpHSL(e,t){this.getHSL(Xi),e.getHSL(Es);const i=Wo(Xi.h,Es.h,t),r=Wo(Xi.s,Es.s,t),a=Wo(Xi.l,Es.l,t);return this.setHSL(i,r,a),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,i=this.g,r=this.b,a=e.elements;return this.r=a[0]*t+a[3]*i+a[6]*r,this.g=a[1]*t+a[4]*i+a[7]*r,this.b=a[2]*t+a[5]*i+a[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const ln=new Ct;Ct.NAMES=Ip;class qE extends En{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new yr,this.environmentIntensity=1,this.environmentRotation=new yr,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}const Bn=new ge,Si=new ge,Qo=new ge,yi=new ge,Gr=new ge,Vr=new ge,rf=new ge,jo=new ge,el=new ge,tl=new ge,nl=new Gt,il=new Gt,rl=new Gt;class Wn{constructor(e=new ge,t=new ge,i=new ge){this.a=e,this.b=t,this.c=i}static getNormal(e,t,i,r){r.subVectors(i,t),Bn.subVectors(e,t),r.cross(Bn);const a=r.lengthSq();return a>0?r.multiplyScalar(1/Math.sqrt(a)):r.set(0,0,0)}static getBarycoord(e,t,i,r,a){Bn.subVectors(r,t),Si.subVectors(i,t),Qo.subVectors(e,t);const o=Bn.dot(Bn),l=Bn.dot(Si),c=Bn.dot(Qo),u=Si.dot(Si),f=Si.dot(Qo),h=o*u-l*l;if(h===0)return a.set(0,0,0),null;const d=1/h,p=(u*c-l*f)*d,m=(o*f-l*c)*d;return a.set(1-p-m,m,p)}static containsPoint(e,t,i,r){return this.getBarycoord(e,t,i,r,yi)===null?!1:yi.x>=0&&yi.y>=0&&yi.x+yi.y<=1}static getInterpolation(e,t,i,r,a,o,l,c){return this.getBarycoord(e,t,i,r,yi)===null?(c.x=0,c.y=0,"z"in c&&(c.z=0),"w"in c&&(c.w=0),null):(c.setScalar(0),c.addScaledVector(a,yi.x),c.addScaledVector(o,yi.y),c.addScaledVector(l,yi.z),c)}static getInterpolatedAttribute(e,t,i,r,a,o){return nl.setScalar(0),il.setScalar(0),rl.setScalar(0),nl.fromBufferAttribute(e,t),il.fromBufferAttribute(e,i),rl.fromBufferAttribute(e,r),o.setScalar(0),o.addScaledVector(nl,a.x),o.addScaledVector(il,a.y),o.addScaledVector(rl,a.z),o}static isFrontFacing(e,t,i,r){return Bn.subVectors(i,t),Si.subVectors(e,t),Bn.cross(Si).dot(r)<0}set(e,t,i){return this.a.copy(e),this.b.copy(t),this.c.copy(i),this}setFromPointsAndIndices(e,t,i,r){return this.a.copy(e[t]),this.b.copy(e[i]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,i,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,i),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Bn.subVectors(this.c,this.b),Si.subVectors(this.a,this.b),Bn.cross(Si).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Wn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Wn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,i,r,a){return Wn.getInterpolation(e,this.a,this.b,this.c,t,i,r,a)}containsPoint(e){return Wn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Wn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const i=this.a,r=this.b,a=this.c;let o,l;Gr.subVectors(r,i),Vr.subVectors(a,i),jo.subVectors(e,i);const c=Gr.dot(jo),u=Vr.dot(jo);if(c<=0&&u<=0)return t.copy(i);el.subVectors(e,r);const f=Gr.dot(el),h=Vr.dot(el);if(f>=0&&h<=f)return t.copy(r);const d=c*h-f*u;if(d<=0&&c>=0&&f<=0)return o=c/(c-f),t.copy(i).addScaledVector(Gr,o);tl.subVectors(e,a);const p=Gr.dot(tl),m=Vr.dot(tl);if(m>=0&&p<=m)return t.copy(a);const E=p*u-c*m;if(E<=0&&u>=0&&m<=0)return l=u/(u-m),t.copy(i).addScaledVector(Vr,l);const g=f*m-p*h;if(g<=0&&h-f>=0&&p-m>=0)return rf.subVectors(a,r),l=(h-f)/(h-f+(p-m)),t.copy(r).addScaledVector(rf,l);const _=1/(g+E+d);return o=E*_,l=d*_,t.copy(i).addScaledVector(Gr,o).addScaledVector(Vr,l)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}class ss{constructor(e=new ge(1/0,1/0,1/0),t=new ge(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,i=e.length;t<i;t+=3)this.expandByPoint(zn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,i=e.count;t<i;t++)this.expandByPoint(zn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,i=e.length;t<i;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const i=zn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(i),this.max.copy(e).add(i),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const i=e.geometry;if(i!==void 0){const a=i.getAttribute("position");if(t===!0&&a!==void 0&&e.isInstancedMesh!==!0)for(let o=0,l=a.count;o<l;o++)e.isMesh===!0?e.getVertexPosition(o,zn):zn.fromBufferAttribute(a,o),zn.applyMatrix4(e.matrixWorld),this.expandByPoint(zn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Ms.copy(e.boundingBox)):(i.boundingBox===null&&i.computeBoundingBox(),Ms.copy(i.boundingBox)),Ms.applyMatrix4(e.matrixWorld),this.union(Ms)}const r=e.children;for(let a=0,o=r.length;a<o;a++)this.expandByObject(r[a],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,zn),zn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,i;return e.normal.x>0?(t=e.normal.x*this.min.x,i=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,i=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,i+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,i+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,i+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,i+=e.normal.z*this.min.z),t<=-e.constant&&i>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Aa),Ts.subVectors(this.max,Aa),Wr.subVectors(e.a,Aa),$r.subVectors(e.b,Aa),Xr.subVectors(e.c,Aa),qi.subVectors($r,Wr),Yi.subVectors(Xr,$r),sr.subVectors(Wr,Xr);let t=[0,-qi.z,qi.y,0,-Yi.z,Yi.y,0,-sr.z,sr.y,qi.z,0,-qi.x,Yi.z,0,-Yi.x,sr.z,0,-sr.x,-qi.y,qi.x,0,-Yi.y,Yi.x,0,-sr.y,sr.x,0];return!al(t,Wr,$r,Xr,Ts)||(t=[1,0,0,0,1,0,0,0,1],!al(t,Wr,$r,Xr,Ts))?!1:(ws.crossVectors(qi,Yi),t=[ws.x,ws.y,ws.z],al(t,Wr,$r,Xr,Ts))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,zn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(zn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Ei[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Ei[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Ei[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Ei[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Ei[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Ei[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Ei[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Ei[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Ei),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(e){return this.min.fromArray(e.min),this.max.fromArray(e.max),this}}const Ei=[new ge,new ge,new ge,new ge,new ge,new ge,new ge,new ge],zn=new ge,Ms=new ss,Wr=new ge,$r=new ge,Xr=new ge,qi=new ge,Yi=new ge,sr=new ge,Aa=new ge,Ts=new ge,ws=new ge,or=new ge;function al(n,e,t,i,r){for(let a=0,o=n.length-3;a<=o;a+=3){or.fromArray(n,a);const l=r.x*Math.abs(or.x)+r.y*Math.abs(or.y)+r.z*Math.abs(or.z),c=e.dot(or),u=t.dot(or),f=i.dot(or);if(Math.max(-Math.max(c,u,f),Math.min(c,u,f))>l)return!1}return!0}const Kt=new ge,As=new xt;let YE=0;class hi extends Ar{constructor(e,t,i=!1){if(super(),Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:YE++}),this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=i,this.usage=Vd,this.updateRanges=[],this.gpuType=ci,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,i){e*=this.itemSize,i*=t.itemSize;for(let r=0,a=this.itemSize;r<a;r++)this.array[e+r]=t.array[i+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,i=this.count;t<i;t++)As.fromBufferAttribute(this,t),As.applyMatrix3(e),this.setXY(t,As.x,As.y);else if(this.itemSize===3)for(let t=0,i=this.count;t<i;t++)Kt.fromBufferAttribute(this,t),Kt.applyMatrix3(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}applyMatrix4(e){for(let t=0,i=this.count;t<i;t++)Kt.fromBufferAttribute(this,t),Kt.applyMatrix4(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}applyNormalMatrix(e){for(let t=0,i=this.count;t<i;t++)Kt.fromBufferAttribute(this,t),Kt.applyNormalMatrix(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}transformDirection(e){for(let t=0,i=this.count;t<i;t++)Kt.fromBufferAttribute(this,t),Kt.transformDirection(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let i=this.array[e*this.itemSize+t];return this.normalized&&(i=Ta(i,this.array)),i}setComponent(e,t,i){return this.normalized&&(i=Sn(i,this.array)),this.array[e*this.itemSize+t]=i,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Ta(t,this.array)),t}setX(e,t){return this.normalized&&(t=Sn(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Ta(t,this.array)),t}setY(e,t){return this.normalized&&(t=Sn(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Ta(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Sn(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Ta(t,this.array)),t}setW(e,t){return this.normalized&&(t=Sn(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,i){return e*=this.itemSize,this.normalized&&(t=Sn(t,this.array),i=Sn(i,this.array)),this.array[e+0]=t,this.array[e+1]=i,this}setXYZ(e,t,i,r){return e*=this.itemSize,this.normalized&&(t=Sn(t,this.array),i=Sn(i,this.array),r=Sn(r,this.array)),this.array[e+0]=t,this.array[e+1]=i,this.array[e+2]=r,this}setXYZW(e,t,i,r,a){return e*=this.itemSize,this.normalized&&(t=Sn(t,this.array),i=Sn(i,this.array),r=Sn(r,this.array),a=Sn(a,this.array)),this.array[e+0]=t,this.array[e+1]=i,this.array[e+2]=r,this.array[e+3]=a,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Vd&&(e.usage=this.usage),e}dispose(){this.dispatchEvent({type:"dispose"})}}class Np extends hi{constructor(e,t,i){super(new Uint16Array(e),t,i)}}class Pp extends hi{constructor(e,t,i){super(new Uint32Array(e),t,i)}}class Dn extends hi{constructor(e,t,i){super(new Float32Array(e),t,i)}}const KE=new ss,Ra=new ge,sl=new ge;class Eu{constructor(e=new ge,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const i=this.center;t!==void 0?i.copy(t):KE.setFromPoints(e).getCenter(i);let r=0;for(let a=0,o=e.length;a<o;a++)r=Math.max(r,i.distanceToSquared(e[a]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const i=this.center.distanceToSquared(e);return t.copy(e),i>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Ra.subVectors(e,this.center);const t=Ra.lengthSq();if(t>this.radius*this.radius){const i=Math.sqrt(t),r=(i-this.radius)*.5;this.center.addScaledVector(Ra,r/i),this.radius+=r}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(sl.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Ra.copy(e.center).add(sl)),this.expandByPoint(Ra.copy(e.center).sub(sl))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(e){return this.radius=e.radius,this.center.fromArray(e.center),this}}let ZE=0;const Pn=new Xt,ol=new En,qr=new ge,An=new ss,Ca=new ss,en=new ge;class vi extends Ar{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:ZE++}),this.uuid=as(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={},this._transformed=!1}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(CE(e)?Pp:Np)(e,1):this.index=e,this}setIndirect(e,t=0){return this.indirect=e,this.indirectOffset=t,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,i=0){this.groups.push({start:e,count:t,materialIndex:i})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const i=this.attributes.normal;if(i!==void 0){const a=new ht().getNormalMatrix(e);i.applyNormalMatrix(a),i.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this._transformed=!0,this}applyQuaternion(e){return Pn.makeRotationFromQuaternion(e),this.applyMatrix4(Pn),this}rotateX(e){return Pn.makeRotationX(e),this.applyMatrix4(Pn),this}rotateY(e){return Pn.makeRotationY(e),this.applyMatrix4(Pn),this}rotateZ(e){return Pn.makeRotationZ(e),this.applyMatrix4(Pn),this}translate(e,t,i){return Pn.makeTranslation(e,t,i),this.applyMatrix4(Pn),this}scale(e,t,i){return Pn.makeScale(e,t,i),this.applyMatrix4(Pn),this}lookAt(e){return ol.lookAt(e),ol.updateMatrix(),this.applyMatrix4(ol.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(qr).negate(),this.translate(qr.x,qr.y,qr.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const i=[];for(let r=0,a=e.length;r<a;r++){const o=e[r];i.push(o.x,o.y,o.z||0)}this.setAttribute("position",new Dn(i,3))}else{const i=Math.min(e.length,t.count);for(let r=0;r<i;r++){const a=e[r];t.setXYZ(r,a.x,a.y,a.z||0)}e.length>t.count&&ut("BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new ss);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){Rt("BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new ge(-1/0,-1/0,-1/0),new ge(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let i=0,r=t.length;i<r;i++){const a=t[i];An.setFromBufferAttribute(a),this.morphTargetsRelative?(en.addVectors(this.boundingBox.min,An.min),this.boundingBox.expandByPoint(en),en.addVectors(this.boundingBox.max,An.max),this.boundingBox.expandByPoint(en)):(this.boundingBox.expandByPoint(An.min),this.boundingBox.expandByPoint(An.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&Rt('BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Eu);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){Rt("BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new ge,1/0);return}if(e){const i=this.boundingSphere.center;if(An.setFromBufferAttribute(e),t)for(let a=0,o=t.length;a<o;a++){const l=t[a];Ca.setFromBufferAttribute(l),this.morphTargetsRelative?(en.addVectors(An.min,Ca.min),An.expandByPoint(en),en.addVectors(An.max,Ca.max),An.expandByPoint(en)):(An.expandByPoint(Ca.min),An.expandByPoint(Ca.max))}An.getCenter(i);let r=0;for(let a=0,o=e.count;a<o;a++)en.fromBufferAttribute(e,a),r=Math.max(r,i.distanceToSquared(en));if(t)for(let a=0,o=t.length;a<o;a++){const l=t[a],c=this.morphTargetsRelative;for(let u=0,f=l.count;u<f;u++)en.fromBufferAttribute(l,u),c&&(qr.fromBufferAttribute(e,u),en.add(qr)),r=Math.max(r,i.distanceToSquared(en))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&Rt('BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){Rt("BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const i=t.position,r=t.normal,a=t.uv;let o=this.getAttribute("tangent");(o===void 0||o.count!==i.count)&&(o=new hi(new Float32Array(4*i.count),4),this.setAttribute("tangent",o));const l=[],c=[];for(let b=0;b<i.count;b++)l[b]=new ge,c[b]=new ge;const u=new ge,f=new ge,h=new ge,d=new xt,p=new xt,m=new xt,E=new ge,g=new ge;function _(b,A,k){u.fromBufferAttribute(i,b),f.fromBufferAttribute(i,A),h.fromBufferAttribute(i,k),d.fromBufferAttribute(a,b),p.fromBufferAttribute(a,A),m.fromBufferAttribute(a,k),f.sub(u),h.sub(u),p.sub(d),m.sub(d);const z=1/(p.x*m.y-m.x*p.y);isFinite(z)&&(E.copy(f).multiplyScalar(m.y).addScaledVector(h,-p.y).multiplyScalar(z),g.copy(h).multiplyScalar(p.x).addScaledVector(f,-m.x).multiplyScalar(z),l[b].add(E),l[A].add(E),l[k].add(E),c[b].add(g),c[A].add(g),c[k].add(g))}let O=this.groups;O.length===0&&(O=[{start:0,count:e.count}]);for(let b=0,A=O.length;b<A;++b){const k=O[b],z=k.start,H=k.count;for(let q=z,Q=z+H;q<Q;q+=3)_(e.getX(q+0),e.getX(q+1),e.getX(q+2))}const D=new ge,y=new ge,B=new ge,R=new ge;function C(b){B.fromBufferAttribute(r,b),R.copy(B);const A=l[b];D.copy(A),D.sub(B.multiplyScalar(B.dot(A))).normalize(),y.crossVectors(R,A);const z=y.dot(c[b])<0?-1:1;o.setXYZW(b,D.x,D.y,D.z,z)}for(let b=0,A=O.length;b<A;++b){const k=O[b],z=k.start,H=k.count;for(let q=z,Q=z+H;q<Q;q+=3)C(e.getX(q+0)),C(e.getX(q+1)),C(e.getX(q+2))}this._transformed=!0}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let i=this.getAttribute("normal");if(i===void 0||i.count!==t.count)i=new hi(new Float32Array(t.count*3),3),this.setAttribute("normal",i);else for(let d=0,p=i.count;d<p;d++)i.setXYZ(d,0,0,0);const r=new ge,a=new ge,o=new ge,l=new ge,c=new ge,u=new ge,f=new ge,h=new ge;if(e)for(let d=0,p=e.count;d<p;d+=3){const m=e.getX(d+0),E=e.getX(d+1),g=e.getX(d+2);r.fromBufferAttribute(t,m),a.fromBufferAttribute(t,E),o.fromBufferAttribute(t,g),f.subVectors(o,a),h.subVectors(r,a),f.cross(h),l.fromBufferAttribute(i,m),c.fromBufferAttribute(i,E),u.fromBufferAttribute(i,g),l.add(f),c.add(f),u.add(f),i.setXYZ(m,l.x,l.y,l.z),i.setXYZ(E,c.x,c.y,c.z),i.setXYZ(g,u.x,u.y,u.z)}else for(let d=0,p=t.count;d<p;d+=3)r.fromBufferAttribute(t,d+0),a.fromBufferAttribute(t,d+1),o.fromBufferAttribute(t,d+2),f.subVectors(o,a),h.subVectors(r,a),f.cross(h),i.setXYZ(d+0,f.x,f.y,f.z),i.setXYZ(d+1,f.x,f.y,f.z),i.setXYZ(d+2,f.x,f.y,f.z);this.normalizeNormals(),i.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,i=e.count;t<i;t++)en.fromBufferAttribute(e,t),en.normalize(),e.setXYZ(t,en.x,en.y,en.z)}toNonIndexed(){function e(l,c){const u=l.array,f=l.itemSize,h=l.normalized,d=new u.constructor(c.length*f);let p=0,m=0;for(let E=0,g=c.length;E<g;E++){l.isInterleavedBufferAttribute?p=c[E]*l.data.stride+l.offset:p=c[E]*f;for(let _=0;_<f;_++)d[m++]=u[p++]}return new hi(d,f,h)}if(this.index===null)return ut("BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new vi,i=this.index.array,r=this.attributes;for(const l in r){const c=r[l],u=e(c,i);t.setAttribute(l,u)}const a=this.morphAttributes;for(const l in a){const c=[],u=a[l];for(let f=0,h=u.length;f<h;f++){const d=u[f],p=e(d,i);c.push(p)}t.morphAttributes[l]=c}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let l=0,c=o.length;l<c;l++){const u=o[l];t.addGroup(u.start,u.count,u.materialIndex)}return t}toJSON(){const e={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.parameters!==void 0&&this._transformed===!0?"BufferGeometry":this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0&&this._transformed!==!0){const c=this.parameters;for(const u in c)c[u]!==void 0&&(e[u]=c[u]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const i=this.attributes;for(const c in i){const u=i[c];e.data.attributes[c]=u.toJSON(e.data)}const r={};let a=!1;for(const c in this.morphAttributes){const u=this.morphAttributes[c],f=[];for(let h=0,d=u.length;h<d;h++){const p=u[h];f.push(p.toJSON(e.data))}f.length>0&&(r[c]=f,a=!0)}a&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const l=this.boundingSphere;return l!==null&&(e.data.boundingSphere=l.toJSON()),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const i=e.index;i!==null&&this.setIndex(i.clone());const r=e.attributes;for(const u in r){const f=r[u];this.setAttribute(u,f.clone(t))}const a=e.morphAttributes;for(const u in a){const f=[],h=a[u];for(let d=0,p=h.length;d<p;d++)f.push(h[d].clone(t));this.morphAttributes[u]=f}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let u=0,f=o.length;u<f;u++){const h=o[u];this.addGroup(h.start,h.count,h.materialIndex)}const l=e.boundingBox;l!==null&&(this.boundingBox=l.clone());const c=e.boundingSphere;return c!==null&&(this.boundingSphere=c.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this._transformed=e._transformed,this}dispose(){this.dispatchEvent({type:"dispose"})}}let JE=0;class So extends Ar{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:JE++}),this.uuid=as(),this.name="",this.type="Material",this.blending=na,this.side=ir,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Pl,this.blendDst=Ll,this.blendEquation=fr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ct(0,0,0),this.blendAlpha=0,this.depthFunc=sa,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Gd,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Or,this.stencilZFail=Or,this.stencilZPass=Or,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const i=e[t];if(i===void 0){ut(`Material: parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){ut(`Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(i):r&&r.isVector2&&i&&i.isVector2||r&&r.isEuler&&i&&i.isEuler||r&&r.isVector3&&i&&i.isVector3?r.copy(i):this[t]=i}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const i={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.color&&this.color.isColor&&(i.color=this.color.getHex()),this.roughness!==void 0&&(i.roughness=this.roughness),this.metalness!==void 0&&(i.metalness=this.metalness),this.sheen!==void 0&&(i.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(i.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(i.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(i.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(i.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(i.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(i.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(i.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(i.shininess=this.shininess),this.clearcoat!==void 0&&(i.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(i.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(i.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(i.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(i.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,i.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(i.sheenColorMap=this.sheenColorMap.toJSON(e).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(i.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(e).uuid),this.dispersion!==void 0&&(i.dispersion=this.dispersion),this.iridescence!==void 0&&(i.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(i.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(i.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(i.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(i.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(i.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(i.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(i.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(i.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(i.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(i.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(i.lightMap=this.lightMap.toJSON(e).uuid,i.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(i.aoMap=this.aoMap.toJSON(e).uuid,i.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(i.bumpMap=this.bumpMap.toJSON(e).uuid,i.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(i.normalMap=this.normalMap.toJSON(e).uuid,i.normalMapType=this.normalMapType,i.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(i.displacementMap=this.displacementMap.toJSON(e).uuid,i.displacementScale=this.displacementScale,i.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(i.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(i.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(i.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(i.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(i.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(i.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(i.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(i.combine=this.combine)),this.envMapRotation!==void 0&&(i.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(i.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(i.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(i.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(i.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(i.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(i.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(i.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(i.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(i.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(i.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(i.size=this.size),this.shadowSide!==null&&(i.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(i.sizeAttenuation=this.sizeAttenuation),this.blending!==na&&(i.blending=this.blending),this.side!==ir&&(i.side=this.side),this.vertexColors===!0&&(i.vertexColors=!0),this.opacity<1&&(i.opacity=this.opacity),this.transparent===!0&&(i.transparent=!0),this.blendSrc!==Pl&&(i.blendSrc=this.blendSrc),this.blendDst!==Ll&&(i.blendDst=this.blendDst),this.blendEquation!==fr&&(i.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(i.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(i.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(i.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(i.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(i.blendAlpha=this.blendAlpha),this.depthFunc!==sa&&(i.depthFunc=this.depthFunc),this.depthTest===!1&&(i.depthTest=this.depthTest),this.depthWrite===!1&&(i.depthWrite=this.depthWrite),this.colorWrite===!1&&(i.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(i.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Gd&&(i.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(i.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(i.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Or&&(i.stencilFail=this.stencilFail),this.stencilZFail!==Or&&(i.stencilZFail=this.stencilZFail),this.stencilZPass!==Or&&(i.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(i.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(i.rotation=this.rotation),this.polygonOffset===!0&&(i.polygonOffset=!0),this.polygonOffsetFactor!==0&&(i.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(i.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(i.linewidth=this.linewidth),this.dashSize!==void 0&&(i.dashSize=this.dashSize),this.gapSize!==void 0&&(i.gapSize=this.gapSize),this.scale!==void 0&&(i.scale=this.scale),this.dithering===!0&&(i.dithering=!0),this.alphaTest>0&&(i.alphaTest=this.alphaTest),this.alphaHash===!0&&(i.alphaHash=!0),this.alphaToCoverage===!0&&(i.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(i.premultipliedAlpha=!0),this.forceSinglePass===!0&&(i.forceSinglePass=!0),this.allowOverride===!1&&(i.allowOverride=!1),this.wireframe===!0&&(i.wireframe=!0),this.wireframeLinewidth>1&&(i.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(i.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(i.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(i.flatShading=!0),this.visible===!1&&(i.visible=!1),this.toneMapped===!1&&(i.toneMapped=!1),this.fog===!1&&(i.fog=!1),Object.keys(this.userData).length>0&&(i.userData=this.userData);function r(a){const o=[];for(const l in a){const c=a[l];delete c.metadata,o.push(c)}return o}if(t){const a=r(e.textures),o=r(e.images);a.length>0&&(i.textures=a),o.length>0&&(i.images=o)}return i}fromJSON(e,t){if(e.uuid!==void 0&&(this.uuid=e.uuid),e.name!==void 0&&(this.name=e.name),e.color!==void 0&&this.color!==void 0&&this.color.setHex(e.color),e.roughness!==void 0&&(this.roughness=e.roughness),e.metalness!==void 0&&(this.metalness=e.metalness),e.sheen!==void 0&&(this.sheen=e.sheen),e.sheenColor!==void 0&&(this.sheenColor=new Ct().setHex(e.sheenColor)),e.sheenRoughness!==void 0&&(this.sheenRoughness=e.sheenRoughness),e.emissive!==void 0&&this.emissive!==void 0&&this.emissive.setHex(e.emissive),e.specular!==void 0&&this.specular!==void 0&&this.specular.setHex(e.specular),e.specularIntensity!==void 0&&(this.specularIntensity=e.specularIntensity),e.specularColor!==void 0&&this.specularColor!==void 0&&this.specularColor.setHex(e.specularColor),e.shininess!==void 0&&(this.shininess=e.shininess),e.clearcoat!==void 0&&(this.clearcoat=e.clearcoat),e.clearcoatRoughness!==void 0&&(this.clearcoatRoughness=e.clearcoatRoughness),e.dispersion!==void 0&&(this.dispersion=e.dispersion),e.iridescence!==void 0&&(this.iridescence=e.iridescence),e.iridescenceIOR!==void 0&&(this.iridescenceIOR=e.iridescenceIOR),e.iridescenceThicknessRange!==void 0&&(this.iridescenceThicknessRange=e.iridescenceThicknessRange),e.transmission!==void 0&&(this.transmission=e.transmission),e.thickness!==void 0&&(this.thickness=e.thickness),e.attenuationDistance!==void 0&&(this.attenuationDistance=e.attenuationDistance),e.attenuationColor!==void 0&&this.attenuationColor!==void 0&&this.attenuationColor.setHex(e.attenuationColor),e.anisotropy!==void 0&&(this.anisotropy=e.anisotropy),e.anisotropyRotation!==void 0&&(this.anisotropyRotation=e.anisotropyRotation),e.fog!==void 0&&(this.fog=e.fog),e.flatShading!==void 0&&(this.flatShading=e.flatShading),e.blending!==void 0&&(this.blending=e.blending),e.combine!==void 0&&(this.combine=e.combine),e.side!==void 0&&(this.side=e.side),e.shadowSide!==void 0&&(this.shadowSide=e.shadowSide),e.opacity!==void 0&&(this.opacity=e.opacity),e.transparent!==void 0&&(this.transparent=e.transparent),e.alphaTest!==void 0&&(this.alphaTest=e.alphaTest),e.alphaHash!==void 0&&(this.alphaHash=e.alphaHash),e.depthFunc!==void 0&&(this.depthFunc=e.depthFunc),e.depthTest!==void 0&&(this.depthTest=e.depthTest),e.depthWrite!==void 0&&(this.depthWrite=e.depthWrite),e.colorWrite!==void 0&&(this.colorWrite=e.colorWrite),e.blendSrc!==void 0&&(this.blendSrc=e.blendSrc),e.blendDst!==void 0&&(this.blendDst=e.blendDst),e.blendEquation!==void 0&&(this.blendEquation=e.blendEquation),e.blendSrcAlpha!==void 0&&(this.blendSrcAlpha=e.blendSrcAlpha),e.blendDstAlpha!==void 0&&(this.blendDstAlpha=e.blendDstAlpha),e.blendEquationAlpha!==void 0&&(this.blendEquationAlpha=e.blendEquationAlpha),e.blendColor!==void 0&&this.blendColor!==void 0&&this.blendColor.setHex(e.blendColor),e.blendAlpha!==void 0&&(this.blendAlpha=e.blendAlpha),e.stencilWriteMask!==void 0&&(this.stencilWriteMask=e.stencilWriteMask),e.stencilFunc!==void 0&&(this.stencilFunc=e.stencilFunc),e.stencilRef!==void 0&&(this.stencilRef=e.stencilRef),e.stencilFuncMask!==void 0&&(this.stencilFuncMask=e.stencilFuncMask),e.stencilFail!==void 0&&(this.stencilFail=e.stencilFail),e.stencilZFail!==void 0&&(this.stencilZFail=e.stencilZFail),e.stencilZPass!==void 0&&(this.stencilZPass=e.stencilZPass),e.stencilWrite!==void 0&&(this.stencilWrite=e.stencilWrite),e.wireframe!==void 0&&(this.wireframe=e.wireframe),e.wireframeLinewidth!==void 0&&(this.wireframeLinewidth=e.wireframeLinewidth),e.wireframeLinecap!==void 0&&(this.wireframeLinecap=e.wireframeLinecap),e.wireframeLinejoin!==void 0&&(this.wireframeLinejoin=e.wireframeLinejoin),e.rotation!==void 0&&(this.rotation=e.rotation),e.linewidth!==void 0&&(this.linewidth=e.linewidth),e.dashSize!==void 0&&(this.dashSize=e.dashSize),e.gapSize!==void 0&&(this.gapSize=e.gapSize),e.scale!==void 0&&(this.scale=e.scale),e.polygonOffset!==void 0&&(this.polygonOffset=e.polygonOffset),e.polygonOffsetFactor!==void 0&&(this.polygonOffsetFactor=e.polygonOffsetFactor),e.polygonOffsetUnits!==void 0&&(this.polygonOffsetUnits=e.polygonOffsetUnits),e.dithering!==void 0&&(this.dithering=e.dithering),e.alphaToCoverage!==void 0&&(this.alphaToCoverage=e.alphaToCoverage),e.premultipliedAlpha!==void 0&&(this.premultipliedAlpha=e.premultipliedAlpha),e.forceSinglePass!==void 0&&(this.forceSinglePass=e.forceSinglePass),e.allowOverride!==void 0&&(this.allowOverride=e.allowOverride),e.visible!==void 0&&(this.visible=e.visible),e.toneMapped!==void 0&&(this.toneMapped=e.toneMapped),e.userData!==void 0&&(this.userData=e.userData),e.vertexColors!==void 0&&(typeof e.vertexColors=="number"?this.vertexColors=e.vertexColors>0:this.vertexColors=e.vertexColors),e.size!==void 0&&(this.size=e.size),e.sizeAttenuation!==void 0&&(this.sizeAttenuation=e.sizeAttenuation),e.map!==void 0&&(this.map=t[e.map]||null),e.matcap!==void 0&&(this.matcap=t[e.matcap]||null),e.alphaMap!==void 0&&(this.alphaMap=t[e.alphaMap]||null),e.bumpMap!==void 0&&(this.bumpMap=t[e.bumpMap]||null),e.bumpScale!==void 0&&(this.bumpScale=e.bumpScale),e.normalMap!==void 0&&(this.normalMap=t[e.normalMap]||null),e.normalMapType!==void 0&&(this.normalMapType=e.normalMapType),e.normalScale!==void 0){let i=e.normalScale;Array.isArray(i)===!1&&(i=[i,i]),this.normalScale=new xt().fromArray(i)}return e.displacementMap!==void 0&&(this.displacementMap=t[e.displacementMap]||null),e.displacementScale!==void 0&&(this.displacementScale=e.displacementScale),e.displacementBias!==void 0&&(this.displacementBias=e.displacementBias),e.roughnessMap!==void 0&&(this.roughnessMap=t[e.roughnessMap]||null),e.metalnessMap!==void 0&&(this.metalnessMap=t[e.metalnessMap]||null),e.emissiveMap!==void 0&&(this.emissiveMap=t[e.emissiveMap]||null),e.emissiveIntensity!==void 0&&(this.emissiveIntensity=e.emissiveIntensity),e.specularMap!==void 0&&(this.specularMap=t[e.specularMap]||null),e.specularIntensityMap!==void 0&&(this.specularIntensityMap=t[e.specularIntensityMap]||null),e.specularColorMap!==void 0&&(this.specularColorMap=t[e.specularColorMap]||null),e.envMap!==void 0&&(this.envMap=t[e.envMap]||null),e.envMapRotation!==void 0&&this.envMapRotation.fromArray(e.envMapRotation),e.envMapIntensity!==void 0&&(this.envMapIntensity=e.envMapIntensity),e.reflectivity!==void 0&&(this.reflectivity=e.reflectivity),e.refractionRatio!==void 0&&(this.refractionRatio=e.refractionRatio),e.lightMap!==void 0&&(this.lightMap=t[e.lightMap]||null),e.lightMapIntensity!==void 0&&(this.lightMapIntensity=e.lightMapIntensity),e.aoMap!==void 0&&(this.aoMap=t[e.aoMap]||null),e.aoMapIntensity!==void 0&&(this.aoMapIntensity=e.aoMapIntensity),e.gradientMap!==void 0&&(this.gradientMap=t[e.gradientMap]||null),e.clearcoatMap!==void 0&&(this.clearcoatMap=t[e.clearcoatMap]||null),e.clearcoatRoughnessMap!==void 0&&(this.clearcoatRoughnessMap=t[e.clearcoatRoughnessMap]||null),e.clearcoatNormalMap!==void 0&&(this.clearcoatNormalMap=t[e.clearcoatNormalMap]||null),e.clearcoatNormalScale!==void 0&&(this.clearcoatNormalScale=new xt().fromArray(e.clearcoatNormalScale)),e.iridescenceMap!==void 0&&(this.iridescenceMap=t[e.iridescenceMap]||null),e.iridescenceThicknessMap!==void 0&&(this.iridescenceThicknessMap=t[e.iridescenceThicknessMap]||null),e.transmissionMap!==void 0&&(this.transmissionMap=t[e.transmissionMap]||null),e.thicknessMap!==void 0&&(this.thicknessMap=t[e.thicknessMap]||null),e.anisotropyMap!==void 0&&(this.anisotropyMap=t[e.anisotropyMap]||null),e.sheenColorMap!==void 0&&(this.sheenColorMap=t[e.sheenColorMap]||null),e.sheenRoughnessMap!==void 0&&(this.sheenRoughnessMap=t[e.sheenRoughnessMap]||null),this}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let i=null;if(t!==null){const r=t.length;i=new Array(r);for(let a=0;a!==r;++a)i[a]=t[a].clone()}return this.clippingPlanes=i,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.allowOverride=e.allowOverride,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}}const Mi=new ge,ll=new ge,Rs=new ge,Ki=new ge,cl=new ge,Cs=new ge,ul=new ge;class QE{constructor(e=new ge,t=new ge(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Mi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const i=t.dot(this.direction);return i<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,i)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Mi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Mi.copy(this.origin).addScaledVector(this.direction,t),Mi.distanceToSquared(e))}distanceSqToSegment(e,t,i,r){ll.copy(e).add(t).multiplyScalar(.5),Rs.copy(t).sub(e).normalize(),Ki.copy(this.origin).sub(ll);const a=e.distanceTo(t)*.5,o=-this.direction.dot(Rs),l=Ki.dot(this.direction),c=-Ki.dot(Rs),u=Ki.lengthSq(),f=Math.abs(1-o*o);let h,d,p,m;if(f>0)if(h=o*c-l,d=o*l-c,m=a*f,h>=0)if(d>=-m)if(d<=m){const E=1/f;h*=E,d*=E,p=h*(h+o*d+2*l)+d*(o*h+d+2*c)+u}else d=a,h=Math.max(0,-(o*d+l)),p=-h*h+d*(d+2*c)+u;else d=-a,h=Math.max(0,-(o*d+l)),p=-h*h+d*(d+2*c)+u;else d<=-m?(h=Math.max(0,-(-o*a+l)),d=h>0?-a:Math.min(Math.max(-a,-c),a),p=-h*h+d*(d+2*c)+u):d<=m?(h=0,d=Math.min(Math.max(-a,-c),a),p=d*(d+2*c)+u):(h=Math.max(0,-(o*a+l)),d=h>0?a:Math.min(Math.max(-a,-c),a),p=-h*h+d*(d+2*c)+u);else d=o>0?-a:a,h=Math.max(0,-(o*d+l)),p=-h*h+d*(d+2*c)+u;return i&&i.copy(this.origin).addScaledVector(this.direction,h),r&&r.copy(ll).addScaledVector(Rs,d),p}intersectSphere(e,t){Mi.subVectors(e.center,this.origin);const i=Mi.dot(this.direction),r=Mi.dot(Mi)-i*i,a=e.radius*e.radius;if(r>a)return null;const o=Math.sqrt(a-r),l=i-o,c=i+o;return c<0?null:l<0?this.at(c,t):this.at(l,t)}intersectsSphere(e){return e.radius<0?!1:this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const i=-(this.origin.dot(e.normal)+e.constant)/t;return i>=0?i:null}intersectPlane(e,t){const i=this.distanceToPlane(e);return i===null?null:this.at(i,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let i,r,a,o,l,c;const u=1/this.direction.x,f=1/this.direction.y,h=1/this.direction.z,d=this.origin;return u>=0?(i=(e.min.x-d.x)*u,r=(e.max.x-d.x)*u):(i=(e.max.x-d.x)*u,r=(e.min.x-d.x)*u),f>=0?(a=(e.min.y-d.y)*f,o=(e.max.y-d.y)*f):(a=(e.max.y-d.y)*f,o=(e.min.y-d.y)*f),i>o||a>r||((a>i||isNaN(i))&&(i=a),(o<r||isNaN(r))&&(r=o),h>=0?(l=(e.min.z-d.z)*h,c=(e.max.z-d.z)*h):(l=(e.max.z-d.z)*h,c=(e.min.z-d.z)*h),i>c||l>r)||((l>i||i!==i)&&(i=l),(c<r||r!==r)&&(r=c),r<0)?null:this.at(i>=0?i:r,t)}intersectsBox(e){return this.intersectBox(e,Mi)!==null}intersectTriangle(e,t,i,r,a){cl.subVectors(t,e),Cs.subVectors(i,e),ul.crossVectors(cl,Cs);let o=this.direction.dot(ul),l;if(o>0){if(r)return null;l=1}else if(o<0)l=-1,o=-o;else return null;Ki.subVectors(this.origin,e);const c=l*this.direction.dot(Cs.crossVectors(Ki,Cs));if(c<0)return null;const u=l*this.direction.dot(cl.cross(Ki));if(u<0||c+u>o)return null;const f=-l*Ki.dot(ul);return f<0?null:this.at(f/o,a)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Lp extends So{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Ct(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new yr,this.combine=fp,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const af=new Xt,lr=new QE,Is=new Eu,sf=new ge,Ns=new ge,Ps=new ge,Ls=new ge,dl=new ge,Ds=new ge,of=new ge,ks=new ge;class gi extends En{constructor(e=new vi,t=new Lp){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,i=Object.keys(t);if(i.length>0){const r=t[i[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let a=0,o=r.length;a<o;a++){const l=r[a].name||String(a);this.morphTargetInfluences.push(0),this.morphTargetDictionary[l]=a}}}}getVertexPosition(e,t){const i=this.geometry,r=i.attributes.position,a=i.morphAttributes.position,o=i.morphTargetsRelative;t.fromBufferAttribute(r,e);const l=this.morphTargetInfluences;if(a&&l){Ds.set(0,0,0);for(let c=0,u=a.length;c<u;c++){const f=l[c],h=a[c];f!==0&&(dl.fromBufferAttribute(h,e),o?Ds.addScaledVector(dl,f):Ds.addScaledVector(dl.sub(t),f))}t.add(Ds)}return t}raycast(e,t){const i=this.geometry,r=this.material,a=this.matrixWorld;r!==void 0&&(i.boundingSphere===null&&i.computeBoundingSphere(),Is.copy(i.boundingSphere),Is.applyMatrix4(a),lr.copy(e.ray).recast(e.near),!(Is.containsPoint(lr.origin)===!1&&(lr.intersectSphere(Is,sf)===null||lr.origin.distanceToSquared(sf)>(e.far-e.near)**2))&&(af.copy(a).invert(),lr.copy(e.ray).applyMatrix4(af),!(i.boundingBox!==null&&lr.intersectsBox(i.boundingBox)===!1)&&this._computeIntersections(e,t,lr)))}_computeIntersections(e,t,i){let r;const a=this.geometry,o=this.material,l=a.index,c=a.attributes.position,u=a.attributes.uv,f=a.attributes.uv1,h=a.attributes.normal,d=a.groups,p=a.drawRange;if(l!==null)if(Array.isArray(o))for(let m=0,E=d.length;m<E;m++){const g=d[m],_=o[g.materialIndex],O=Math.max(g.start,p.start),D=Math.min(l.count,Math.min(g.start+g.count,p.start+p.count));for(let y=O,B=D;y<B;y+=3){const R=l.getX(y),C=l.getX(y+1),b=l.getX(y+2);r=Us(this,_,e,i,u,f,h,R,C,b),r&&(r.faceIndex=Math.floor(y/3),r.face.materialIndex=g.materialIndex,t.push(r))}}else{const m=Math.max(0,p.start),E=Math.min(l.count,p.start+p.count);for(let g=m,_=E;g<_;g+=3){const O=l.getX(g),D=l.getX(g+1),y=l.getX(g+2);r=Us(this,o,e,i,u,f,h,O,D,y),r&&(r.faceIndex=Math.floor(g/3),t.push(r))}}else if(c!==void 0)if(Array.isArray(o))for(let m=0,E=d.length;m<E;m++){const g=d[m],_=o[g.materialIndex],O=Math.max(g.start,p.start),D=Math.min(c.count,Math.min(g.start+g.count,p.start+p.count));for(let y=O,B=D;y<B;y+=3){const R=y,C=y+1,b=y+2;r=Us(this,_,e,i,u,f,h,R,C,b),r&&(r.faceIndex=Math.floor(y/3),r.face.materialIndex=g.materialIndex,t.push(r))}}else{const m=Math.max(0,p.start),E=Math.min(c.count,p.start+p.count);for(let g=m,_=E;g<_;g+=3){const O=g,D=g+1,y=g+2;r=Us(this,o,e,i,u,f,h,O,D,y),r&&(r.faceIndex=Math.floor(g/3),t.push(r))}}}}function jE(n,e,t,i,r,a,o,l){let c;if(e.side===yn?c=i.intersectTriangle(o,a,r,!0,l):c=i.intersectTriangle(r,a,o,e.side===ir,l),c===null)return null;ks.copy(l),ks.applyMatrix4(n.matrixWorld);const u=t.ray.origin.distanceTo(ks);return u<t.near||u>t.far?null:{distance:u,point:ks.clone(),object:n}}function Us(n,e,t,i,r,a,o,l,c,u){n.getVertexPosition(l,Ns),n.getVertexPosition(c,Ps),n.getVertexPosition(u,Ls);const f=jE(n,e,t,i,Ns,Ps,Ls,of);if(f){const h=new ge;Wn.getBarycoord(of,Ns,Ps,Ls,h),r&&(f.uv=Wn.getInterpolatedAttribute(r,l,c,u,h,new xt)),a&&(f.uv1=Wn.getInterpolatedAttribute(a,l,c,u,h,new xt)),o&&(f.normal=Wn.getInterpolatedAttribute(o,l,c,u,h,new ge),f.normal.dot(i.direction)>0&&f.normal.multiplyScalar(-1));const d={a:l,b:c,c:u,normal:new ge,materialIndex:0};Wn.getNormal(Ns,Ps,Ls,d.normal),f.face=d,f.barycoord=h}return f}class eM extends _n{constructor(e=null,t=1,i=1,r,a,o,l,c,u=an,f=an,h,d){super(null,o,l,c,u,f,r,a,h,d),this.isDataTexture=!0,this.image={data:e,width:t,height:i},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const fl=new ge,tM=new ge,nM=new ht;class ur{constructor(e=new ge(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,i,r){return this.normal.set(e,t,i),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,i){const r=fl.subVectors(i,t).cross(tM.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t,i=!0){const r=e.delta(fl),a=this.normal.dot(r);if(a===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const o=-(e.start.dot(this.normal)+this.constant)/a;return i===!0&&(o<0||o>1)?null:t.copy(e.start).addScaledVector(r,o)}intersectsLine(e){const t=this.distanceToPoint(e.start),i=this.distanceToPoint(e.end);return t<0&&i>0||i<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const i=t||nM.getNormalMatrix(e),r=this.coplanarPoint(fl).applyMatrix4(e),a=this.normal.applyMatrix3(i).normalize();return this.constant=-r.dot(a),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const cr=new Eu,iM=new xt(.5,.5),Os=new ge;class Mu{constructor(e=new ur,t=new ur,i=new ur,r=new ur,a=new ur,o=new ur){this.planes=[e,t,i,r,a,o]}set(e,t,i,r,a,o){const l=this.planes;return l[0].copy(e),l[1].copy(t),l[2].copy(i),l[3].copy(r),l[4].copy(a),l[5].copy(o),this}copy(e){const t=this.planes;for(let i=0;i<6;i++)t[i].copy(e.planes[i]);return this}setFromProjectionMatrix(e,t=ui,i=!1){const r=this.planes,a=e.elements,o=a[0],l=a[1],c=a[2],u=a[3],f=a[4],h=a[5],d=a[6],p=a[7],m=a[8],E=a[9],g=a[10],_=a[11],O=a[12],D=a[13],y=a[14],B=a[15];if(r[0].setComponents(u-o,p-f,_-m,B-O).normalize(),r[1].setComponents(u+o,p+f,_+m,B+O).normalize(),r[2].setComponents(u+l,p+h,_+E,B+D).normalize(),r[3].setComponents(u-l,p-h,_-E,B-D).normalize(),i)r[4].setComponents(c,d,g,y).normalize(),r[5].setComponents(u-c,p-d,_-g,B-y).normalize();else if(r[4].setComponents(u-c,p-d,_-g,B-y).normalize(),t===ui)r[5].setComponents(u+c,p+d,_+g,B+y).normalize();else if(t===Qa)r[5].setComponents(c,d,g,y).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),cr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),cr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(cr)}intersectsSprite(e){cr.center.set(0,0,0);const t=iM.distanceTo(e.center);return cr.radius=.7071067811865476+t,cr.applyMatrix4(e.matrixWorld),this.intersectsSphere(cr)}intersectsSphere(e){const t=this.planes,i=e.center,r=-e.radius;for(let a=0;a<6;a++)if(t[a].distanceToPoint(i)<r)return!1;return!0}intersectsBox(e){const t=this.planes;for(let i=0;i<6;i++){const r=t[i];if(Os.x=r.normal.x>0?e.max.x:e.min.x,Os.y=r.normal.y>0?e.max.y:e.min.y,Os.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint(Os)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let i=0;i<6;i++)if(t[i].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class Dp extends _n{constructor(e=[],t=br,i,r,a,o,l,c,u,f){super(e,t,i,r,a,o,l,c,u,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class la extends _n{constructor(e,t,i=mi,r,a,o,l=an,c=an,u,f=Ui,h=1){if(f!==Ui&&f!==mr)throw new Error("THREE.DepthTexture: format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const d={width:e,height:t,depth:h};super(d,r,a,o,l,c,f,i,u),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.source=new yu(Object.assign({},e.image)),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}class rM extends la{constructor(e,t=mi,i=br,r,a,o=an,l=an,c,u=Ui){const f={width:e,height:e,depth:1},h=[f,f,f,f,f,f];super(e,e,t,i,r,a,o,l,c,u),this.image=h,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(e){this.image=e}}class kp extends _n{constructor(e=null){super(),this.sourceTexture=e,this.isExternalTexture=!0}copy(e){return super.copy(e),this.sourceTexture=e.sourceTexture,this}}class os extends vi{constructor(e=1,t=1,i=1,r=1,a=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:i,widthSegments:r,heightSegments:a,depthSegments:o};const l=this;r=Math.floor(r),a=Math.floor(a),o=Math.floor(o);const c=[],u=[],f=[],h=[];let d=0,p=0;m("z","y","x",-1,-1,i,t,e,o,a,0),m("z","y","x",1,-1,i,t,-e,o,a,1),m("x","z","y",1,1,e,i,t,r,o,2),m("x","z","y",1,-1,e,i,-t,r,o,3),m("x","y","z",1,-1,e,t,i,r,a,4),m("x","y","z",-1,-1,e,t,-i,r,a,5),this.setIndex(c),this.setAttribute("position",new Dn(u,3)),this.setAttribute("normal",new Dn(f,3)),this.setAttribute("uv",new Dn(h,2));function m(E,g,_,O,D,y,B,R,C,b,A){const k=y/C,z=B/b,H=y/2,q=B/2,Q=R/2,G=C+1,T=b+1;let w=0,I=0;const F=new ge;for(let Y=0;Y<T;Y++){const te=Y*z-q;for(let X=0;X<G;X++){const K=X*k-H;F[E]=K*O,F[g]=te*D,F[_]=Q,u.push(F.x,F.y,F.z),F[E]=0,F[g]=0,F[_]=R>0?1:-1,f.push(F.x,F.y,F.z),h.push(X/C),h.push(1-Y/b),w+=1}}for(let Y=0;Y<b;Y++)for(let te=0;te<C;te++){const X=d+te+G*Y,K=d+te+G*(Y+1),se=d+(te+1)+G*(Y+1),ne=d+(te+1)+G*Y;c.push(X,K,ne),c.push(K,se,ne),I+=6}l.addGroup(p,I,A),p+=I,d+=w}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new os(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}class Tu extends vi{constructor(e=[],t=[],i=1,r=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:i,detail:r};const a=[],o=[];l(r),u(i),f(),this.setAttribute("position",new Dn(a,3)),this.setAttribute("normal",new Dn(a.slice(),3)),this.setAttribute("uv",new Dn(o,2)),r===0?this.computeVertexNormals():this.normalizeNormals();function l(O){const D=new ge,y=new ge,B=new ge;for(let R=0;R<t.length;R+=3)p(t[R+0],D),p(t[R+1],y),p(t[R+2],B),c(D,y,B,O)}function c(O,D,y,B){const R=B+1,C=[];for(let b=0;b<=R;b++){C[b]=[];const A=O.clone().lerp(y,b/R),k=D.clone().lerp(y,b/R),z=R-b;for(let H=0;H<=z;H++)H===0&&b===R?C[b][H]=A:C[b][H]=A.clone().lerp(k,H/z)}for(let b=0;b<R;b++)for(let A=0;A<2*(R-b)-1;A++){const k=Math.floor(A/2);A%2===0?(d(C[b][k+1]),d(C[b+1][k]),d(C[b][k])):(d(C[b][k+1]),d(C[b+1][k+1]),d(C[b+1][k]))}}function u(O){const D=new ge;for(let y=0;y<a.length;y+=3)D.x=a[y+0],D.y=a[y+1],D.z=a[y+2],D.normalize().multiplyScalar(O),a[y+0]=D.x,a[y+1]=D.y,a[y+2]=D.z}function f(){const O=new ge;for(let D=0;D<a.length;D+=3){O.x=a[D+0],O.y=a[D+1],O.z=a[D+2];const y=g(O)/2/Math.PI+.5,B=_(O)/Math.PI+.5;o.push(y,1-B)}m(),h()}function h(){for(let O=0;O<o.length;O+=6){const D=o[O+0],y=o[O+2],B=o[O+4],R=Math.max(D,y,B),C=Math.min(D,y,B);R>.9&&C<.1&&(D<.2&&(o[O+0]+=1),y<.2&&(o[O+2]+=1),B<.2&&(o[O+4]+=1))}}function d(O){a.push(O.x,O.y,O.z)}function p(O,D){const y=O*3;D.x=e[y+0],D.y=e[y+1],D.z=e[y+2]}function m(){const O=new ge,D=new ge,y=new ge,B=new ge,R=new xt,C=new xt,b=new xt;for(let A=0,k=0;A<a.length;A+=9,k+=6){O.set(a[A+0],a[A+1],a[A+2]),D.set(a[A+3],a[A+4],a[A+5]),y.set(a[A+6],a[A+7],a[A+8]),R.set(o[k+0],o[k+1]),C.set(o[k+2],o[k+3]),b.set(o[k+4],o[k+5]),B.copy(O).add(D).add(y).divideScalar(3);const z=g(B);E(R,k+0,O,z),E(C,k+2,D,z),E(b,k+4,y,z)}}function E(O,D,y,B){B<0&&O.x===1&&(o[D]=O.x-1),y.x===0&&y.z===0&&(o[D]=B/2/Math.PI+.5)}function g(O){return Math.atan2(O.z,-O.x)}function _(O){return Math.atan2(-O.y,Math.sqrt(O.x*O.x+O.z*O.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Tu(e.vertices,e.indices,e.radius,e.detail)}}class wu extends Tu{constructor(e=1,t=0){const i=(1+Math.sqrt(5))/2,r=[-1,i,0,1,i,0,-1,-i,0,1,-i,0,0,-1,i,0,1,i,0,-1,-i,0,1,-i,i,0,-1,i,0,1,-i,0,-1,-i,0,1],a=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(r,a,e,t),this.type="IcosahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new wu(e.radius,e.detail)}}class yo extends vi{constructor(e=1,t=1,i=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:i,heightSegments:r};const a=e/2,o=t/2,l=Math.floor(i),c=Math.floor(r),u=l+1,f=c+1,h=e/l,d=t/c,p=[],m=[],E=[],g=[];for(let _=0;_<f;_++){const O=_*d-o;for(let D=0;D<u;D++){const y=D*h-a;m.push(y,-O,0),E.push(0,0,1),g.push(D/l),g.push(1-_/c)}}for(let _=0;_<c;_++)for(let O=0;O<l;O++){const D=O+u*_,y=O+u*(_+1),B=O+1+u*(_+1),R=O+1+u*_;p.push(D,y,R),p.push(y,B,R)}this.setIndex(p),this.setAttribute("position",new Dn(m,3)),this.setAttribute("normal",new Dn(E,3)),this.setAttribute("uv",new Dn(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new yo(e.width,e.height,e.widthSegments,e.heightSegments)}}function ca(n){const e={};for(const t in n){e[t]={};for(const i in n[t]){const r=n[t][i];if(lf(r))r.isRenderTargetTexture?(ut("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][i]=null):e[t][i]=r.clone();else if(Array.isArray(r))if(lf(r[0])){const a=[];for(let o=0,l=r.length;o<l;o++)a[o]=r[o].clone();e[t][i]=a}else e[t][i]=r.slice();else e[t][i]=r}}return e}function mn(n){const e={};for(let t=0;t<n.length;t++){const i=ca(n[t]);for(const r in i)e[r]=i[r]}return e}function lf(n){return n&&(n.isColor||n.isMatrix3||n.isMatrix4||n.isVector2||n.isVector3||n.isVector4||n.isTexture||n.isQuaternion)}function aM(n){const e=[];for(let t=0;t<n.length;t++)e.push(n[t].clone());return e}function Up(n){const e=n.getRenderTarget();return e===null?n.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:bt.workingColorSpace}const sM={clone:ca,merge:mn};var oM=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,lM=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Kn extends So{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=oM,this.fragmentShader=lM,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ca(e.uniforms),this.uniformsGroups=aM(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this.defaultAttributeValues=Object.assign({},e.defaultAttributeValues),this.index0AttributeName=e.index0AttributeName,this.uniformsNeedUpdate=e.uniformsNeedUpdate,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const r in this.uniforms){const o=this.uniforms[r].value;o&&o.isTexture?t.uniforms[r]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[r]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[r]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[r]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[r]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[r]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[r]={type:"m4",value:o.toArray()}:t.uniforms[r]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const i={};for(const r in this.extensions)this.extensions[r]===!0&&(i[r]=!0);return Object.keys(i).length>0&&(t.extensions=i),t}fromJSON(e,t){if(super.fromJSON(e,t),e.uniforms!==void 0)for(const i in e.uniforms){const r=e.uniforms[i];switch(this.uniforms[i]={},r.type){case"t":this.uniforms[i].value=t[r.value]||null;break;case"c":this.uniforms[i].value=new Ct().setHex(r.value);break;case"v2":this.uniforms[i].value=new xt().fromArray(r.value);break;case"v3":this.uniforms[i].value=new ge().fromArray(r.value);break;case"v4":this.uniforms[i].value=new Gt().fromArray(r.value);break;case"m3":this.uniforms[i].value=new ht().fromArray(r.value);break;case"m4":this.uniforms[i].value=new Xt().fromArray(r.value);break;default:this.uniforms[i].value=r.value}}if(e.defines!==void 0&&(this.defines=e.defines),e.vertexShader!==void 0&&(this.vertexShader=e.vertexShader),e.fragmentShader!==void 0&&(this.fragmentShader=e.fragmentShader),e.glslVersion!==void 0&&(this.glslVersion=e.glslVersion),e.extensions!==void 0)for(const i in e.extensions)this.extensions[i]=e.extensions[i];return e.lights!==void 0&&(this.lights=e.lights),e.clipping!==void 0&&(this.clipping=e.clipping),this}}class cM extends Kn{constructor(e){super(e),this.isRawShaderMaterial=!0,this.type="RawShaderMaterial"}}class uM extends So{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=SE,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class dM extends So{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}class Op extends En{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Ct(e),this.intensity=t}dispose(){this.dispatchEvent({type:"dispose"})}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,t}}const hl=new Xt,cf=new ge,uf=new ge;class fM{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.biasNode=null,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new xt(512,512),this.mapType=In,this.map=null,this.mapPass=null,this.matrix=new Xt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Mu,this._frameExtents=new xt(1,1),this._viewportCount=1,this._viewports=[new Gt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,i=this.matrix;cf.setFromMatrixPosition(e.matrixWorld),t.position.copy(cf),uf.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(uf),t.updateMatrixWorld(),hl.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(hl,t.coordinateSystem,t.reversedDepth),t.coordinateSystem===Qa||t.reversedDepth?i.set(.5,0,0,.5,0,.5,0,.5,0,0,1,0,0,0,0,1):i.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),i.multiply(hl)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.autoUpdate=e.autoUpdate,this.needsUpdate=e.needsUpdate,this.normalBias=e.normalBias,this.blurSamples=e.blurSamples,this.mapSize.copy(e.mapSize),this.biasNode=e.biasNode,this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}const Fs=new ge,Bs=new ha,ei=new ge;class Fp extends En{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Xt,this.projectionMatrix=new Xt,this.projectionMatrixInverse=new Xt,this.coordinateSystem=ui,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorld.decompose(Fs,Bs,ei),ei.x===1&&ei.y===1&&ei.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Fs,Bs,ei.set(1,1,1)).invert()}updateWorldMatrix(e,t,i=!1){super.updateWorldMatrix(e,t,i),this.matrixWorld.decompose(Fs,Bs,ei),ei.x===1&&ei.y===1&&ei.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Fs,Bs,ei.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}}const Zi=new ge,df=new xt,ff=new xt;class Cn extends Fp{constructor(e=50,t=1,i=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=i,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=xc*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Vo*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return xc*2*Math.atan(Math.tan(Vo*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,i){Zi.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Zi.x,Zi.y).multiplyScalar(-e/Zi.z),Zi.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),i.set(Zi.x,Zi.y).multiplyScalar(-e/Zi.z)}getViewSize(e,t){return this.getViewBounds(e,df,ff),t.subVectors(ff,df)}setViewOffset(e,t,i,r,a,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=i,this.view.offsetY=r,this.view.width=a,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Vo*.5*this.fov)/this.zoom,i=2*t,r=this.aspect*i,a=-.5*r;const o=this.view;if(this.view!==null&&this.view.enabled){const c=o.fullWidth,u=o.fullHeight;a+=o.offsetX*r/c,t-=o.offsetY*i/u,r*=o.width/c,i*=o.height/u}const l=this.filmOffset;l!==0&&(a+=e*l/this.getFilmWidth()),this.projectionMatrix.makePerspective(a,a+r,t,t-i,e,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}class hM extends fM{constructor(){super(new Cn(90,1,.5,500)),this.isPointLightShadow=!0}}class hf extends Op{constructor(e,t,i=0,r=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=i,this.decay=r,this.shadow=new hM}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){super.dispose(),this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}toJSON(e){const t=super.toJSON(e);return t.object.distance=this.distance,t.object.decay=this.decay,t.object.shadow=this.shadow.toJSON(),t}}class Bp extends Fp{constructor(e=-1,t=1,i=1,r=-1,a=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=i,this.bottom=r,this.near=a,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,i,r,a,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=i,this.view.offsetY=r,this.view.width=a,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),i=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let a=i-e,o=i+e,l=r+t,c=r-t;if(this.view!==null&&this.view.enabled){const u=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;a+=u*this.view.offsetX,o=a+u*this.view.width,l-=f*this.view.offsetY,c=l-f*this.view.height}this.projectionMatrix.makeOrthographic(a,o,l,c,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}class pM extends Op{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Yr=-90,Kr=1;class mM extends En{constructor(e,t,i){super(),this.type="CubeCamera",this.renderTarget=i,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new Cn(Yr,Kr,e,t);r.layers=this.layers,this.add(r);const a=new Cn(Yr,Kr,e,t);a.layers=this.layers,this.add(a);const o=new Cn(Yr,Kr,e,t);o.layers=this.layers,this.add(o);const l=new Cn(Yr,Kr,e,t);l.layers=this.layers,this.add(l);const c=new Cn(Yr,Kr,e,t);c.layers=this.layers,this.add(c);const u=new Cn(Yr,Kr,e,t);u.layers=this.layers,this.add(u)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[i,r,a,o,l,c]=t;for(const u of t)this.remove(u);if(e===ui)i.up.set(0,1,0),i.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),a.up.set(0,0,-1),a.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),l.up.set(0,1,0),l.lookAt(0,0,1),c.up.set(0,1,0),c.lookAt(0,0,-1);else if(e===Qa)i.up.set(0,-1,0),i.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),a.up.set(0,0,1),a.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),l.up.set(0,-1,0),l.lookAt(0,0,1),c.up.set(0,-1,0),c.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const u of t)this.add(u),u.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:i,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[a,o,l,c,u,f]=this.children,h=e.getRenderTarget(),d=e.getActiveCubeFace(),p=e.getActiveMipmapLevel(),m=e.xr.enabled;e.xr.enabled=!1;const E=i.texture.generateMipmaps;i.texture.generateMipmaps=!1;let g=!1;e.isWebGLRenderer===!0?g=e.state.buffers.depth.getReversed():g=e.reversedDepthBuffer,e.setRenderTarget(i,0,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,a),e.setRenderTarget(i,1,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,o),e.setRenderTarget(i,2,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,l),e.setRenderTarget(i,3,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,c),e.setRenderTarget(i,4,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,u),i.texture.generateMipmaps=E,e.setRenderTarget(i,5,r),g&&e.autoClear===!1&&e.clearDepth(),e.render(t,f),e.setRenderTarget(h,d,p),e.xr.enabled=m,i.texture.needsPMREMUpdate=!0}}class gM extends Cn{constructor(e=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=e}}const Pu=class Pu{constructor(e,t,i,r){this.elements=[1,0,0,1],e!==void 0&&this.set(e,t,i,r)}identity(){return this.set(1,0,0,1),this}fromArray(e,t=0){for(let i=0;i<4;i++)this.elements[i]=e[i+t];return this}set(e,t,i,r){const a=this.elements;return a[0]=e,a[2]=t,a[1]=i,a[3]=r,this}};Pu.prototype.isMatrix2=!0;let pf=Pu;function mf(n,e,t,i){const r=_M(i);switch(t){case Mp:return n*e;case wp:return n*e/r.components*r.byteLength;case _u:return n*e/r.components*r.byteLength;case Sr:return n*e*2/r.components*r.byteLength;case vu:return n*e*2/r.components*r.byteLength;case Tp:return n*e*3/r.components*r.byteLength;case Xn:return n*e*4/r.components*r.byteLength;case xu:return n*e*4/r.components*r.byteLength;case Ws:case $s:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*8;case Xs:case qs:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case Wl:case Xl:return Math.max(n,16)*Math.max(e,8)/4;case Vl:case $l:return Math.max(n,8)*Math.max(e,8)/2;case ql:case Yl:case Zl:case Jl:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*8;case Kl:case ao:case Ql:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case jl:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case ec:return Math.floor((n+4)/5)*Math.floor((e+3)/4)*16;case tc:return Math.floor((n+4)/5)*Math.floor((e+4)/5)*16;case nc:return Math.floor((n+5)/6)*Math.floor((e+4)/5)*16;case ic:return Math.floor((n+5)/6)*Math.floor((e+5)/6)*16;case rc:return Math.floor((n+7)/8)*Math.floor((e+4)/5)*16;case ac:return Math.floor((n+7)/8)*Math.floor((e+5)/6)*16;case sc:return Math.floor((n+7)/8)*Math.floor((e+7)/8)*16;case oc:return Math.floor((n+9)/10)*Math.floor((e+4)/5)*16;case lc:return Math.floor((n+9)/10)*Math.floor((e+5)/6)*16;case cc:return Math.floor((n+9)/10)*Math.floor((e+7)/8)*16;case uc:return Math.floor((n+9)/10)*Math.floor((e+9)/10)*16;case dc:return Math.floor((n+11)/12)*Math.floor((e+9)/10)*16;case fc:return Math.floor((n+11)/12)*Math.floor((e+11)/12)*16;case hc:case pc:case mc:return Math.ceil(n/4)*Math.ceil(e/4)*16;case gc:case _c:return Math.ceil(n/4)*Math.ceil(e/4)*8;case so:case vc:return Math.ceil(n/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function _M(n){switch(n){case In:case bp:return{byteLength:1,components:1};case Za:case Sp:case ki:return{byteLength:2,components:1};case mu:case gu:return{byteLength:2,components:4};case mi:case pu:case ci:return{byteLength:4,components:1};case yp:case Ep:return{byteLength:4,components:3}}throw new Error(`THREE.TextureUtils: Unknown texture type ${n}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:fu}}));typeof window<"u"&&(window.__THREE__?ut("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=fu);/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function zp(){let n=null,e=!1,t=null,i=null;function r(a,o){t(a,o),i=n.requestAnimationFrame(r)}return{start:function(){e!==!0&&t!==null&&n!==null&&(i=n.requestAnimationFrame(r),e=!0)},stop:function(){n!==null&&n.cancelAnimationFrame(i),e=!1},setAnimationLoop:function(a){t=a},setContext:function(a){n=a}}}function vM(n){const e=new WeakMap;function t(l,c){const u=l.array,f=l.usage,h=u.byteLength,d=n.createBuffer();n.bindBuffer(c,d),n.bufferData(c,u,f),l.onUploadCallback();let p;if(u instanceof Float32Array)p=n.FLOAT;else if(typeof Float16Array<"u"&&u instanceof Float16Array)p=n.HALF_FLOAT;else if(u instanceof Uint16Array)l.isFloat16BufferAttribute?p=n.HALF_FLOAT:p=n.UNSIGNED_SHORT;else if(u instanceof Int16Array)p=n.SHORT;else if(u instanceof Uint32Array)p=n.UNSIGNED_INT;else if(u instanceof Int32Array)p=n.INT;else if(u instanceof Int8Array)p=n.BYTE;else if(u instanceof Uint8Array)p=n.UNSIGNED_BYTE;else if(u instanceof Uint8ClampedArray)p=n.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+u);return{buffer:d,type:p,bytesPerElement:u.BYTES_PER_ELEMENT,version:l.version,size:h}}function i(l,c,u){const f=c.array,h=c.updateRanges;if(n.bindBuffer(u,l),h.length===0)n.bufferSubData(u,0,f);else{h.sort((p,m)=>p.start-m.start);let d=0;for(let p=1;p<h.length;p++){const m=h[d],E=h[p];E.start<=m.start+m.count+1?m.count=Math.max(m.count,E.start+E.count-m.start):(++d,h[d]=E)}h.length=d+1;for(let p=0,m=h.length;p<m;p++){const E=h[p];n.bufferSubData(u,E.start*f.BYTES_PER_ELEMENT,f,E.start,E.count)}c.clearUpdateRanges()}c.onUploadCallback()}function r(l){return l.isInterleavedBufferAttribute&&(l=l.data),e.get(l)}function a(l){l.isInterleavedBufferAttribute&&(l=l.data);const c=e.get(l);c&&(n.deleteBuffer(c.buffer),e.delete(l))}function o(l,c){if(l.isInterleavedBufferAttribute&&(l=l.data),l.isGLBufferAttribute){const f=e.get(l);(!f||f.version<l.version)&&e.set(l,{buffer:l.buffer,type:l.type,bytesPerElement:l.elementSize,version:l.version});return}const u=e.get(l);if(u===void 0)e.set(l,t(l,c));else if(u.version<l.version){if(u.size!==l.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");i(u.buffer,l,c),u.version=l.version}}return{get:r,remove:a,update:o}}var xM=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,bM=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,SM=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,yM=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,EM=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,MM=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,TM=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,wM=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,AM=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,RM=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,CM=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,IM=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,NM=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,PM=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,LM=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,DM=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,kM=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,UM=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,OM=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,FM=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,BM=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,zM=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,HM=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,GM=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
#define inverseTransformDirection transformDirectionByInverseViewMatrix
vec3 transformNormalByInverseViewMatrix( in vec3 normal, in mat4 viewMatrix ) {
	return normalize( ( vec4( normal, 0.0 ) * viewMatrix ).xyz );
}
vec3 transformDirectionByInverseViewMatrix( in vec3 dir, in mat4 viewMatrix ) {
	return normalize( ( vec4( dir, 0.0 ) * viewMatrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,VM=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,WM=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
#endif`,$M=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,XM=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,qM=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,YM=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,KM="gl_FragColor = linearToOutputTexel( gl_FragColor );",ZM=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,JM=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * reflectVec );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,QM=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,jM=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,eT=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,tT=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,nT=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,iT=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,rT=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,aT=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,sT=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,oT=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,lT=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,cT=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,uT=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif
#include <lightprobes_pars_fragment>`,dT=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = transformDirectionByInverseViewMatrix( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,fT=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,hT=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,pT=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,mT=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,gT=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,_T=`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		return 0.5 / max( gv + gl, EPSILON );
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,vT=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
	#ifdef USE_LIGHT_PROBES_GRID
		vec3 probeWorldPos = ( ( vec4( geometryPosition, 1.0 ) - viewMatrix[ 3 ] ) * viewMatrix ).xyz;
		vec3 probeWorldNormal = transformNormalByInverseViewMatrix( geometryNormal, viewMatrix );
		irradiance += getLightProbeGridIrradiance( probeWorldPos, probeWorldNormal );
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,xT=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,bT=`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,ST=`#ifdef USE_LIGHT_PROBES_GRID
uniform highp sampler3D probesSH;
uniform vec3 probesMin;
uniform vec3 probesMax;
uniform vec3 probesResolution;
vec3 getLightProbeGridIrradiance( vec3 worldPos, vec3 worldNormal ) {
	vec3 res = probesResolution;
	vec3 gridRange = probesMax - probesMin;
	vec3 resMinusOne = res - 1.0;
	vec3 probeSpacing = gridRange / resMinusOne;
	vec3 samplePos = worldPos + worldNormal * probeSpacing * 0.5;
	vec3 uvw = clamp( ( samplePos - probesMin ) / gridRange, 0.0, 1.0 );
	uvw = uvw * resMinusOne / res + 0.5 / res;
	float nz          = res.z;
	float paddedSlices = nz + 2.0;
	float atlasDepth  = 7.0 * paddedSlices;
	float uvZBase     = uvw.z * nz + 1.0;
	vec4 s0 = texture( probesSH, vec3( uvw.xy, ( uvZBase                       ) / atlasDepth ) );
	vec4 s1 = texture( probesSH, vec3( uvw.xy, ( uvZBase +       paddedSlices   ) / atlasDepth ) );
	vec4 s2 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 2.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s3 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 3.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s4 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 4.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s5 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 5.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s6 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 6.0 * paddedSlices   ) / atlasDepth ) );
	vec3 c0 = s0.xyz;
	vec3 c1 = vec3( s0.w, s1.xy );
	vec3 c2 = vec3( s1.zw, s2.x );
	vec3 c3 = s2.yzw;
	vec3 c4 = s3.xyz;
	vec3 c5 = vec3( s3.w, s4.xy );
	vec3 c6 = vec3( s4.zw, s5.x );
	vec3 c7 = s5.yzw;
	vec3 c8 = s6.xyz;
	float x = worldNormal.x, y = worldNormal.y, z = worldNormal.z;
	vec3 result = c0 * 0.886227;
	result += c1 * 2.0 * 0.511664 * y;
	result += c2 * 2.0 * 0.511664 * z;
	result += c3 * 2.0 * 0.511664 * x;
	result += c4 * 2.0 * 0.429043 * x * y;
	result += c5 * 2.0 * 0.429043 * y * z;
	result += c6 * ( 0.743125 * z * z - 0.247708 );
	result += c7 * 2.0 * 0.429043 * x * z;
	result += c8 * 0.429043 * ( x * x - y * y );
	return max( result, vec3( 0.0 ) );
}
#endif`,yT=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,ET=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,MT=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,TT=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,wT=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,AT=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,RT=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,CT=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,IT=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,NT=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,PT=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,LT=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,DT=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,kT=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,UT=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,OT=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#ifdef DOUBLE_SIDED
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#ifdef DOUBLE_SIDED
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,FT=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#if defined( USE_PACKED_NORMALMAP )
		mapN = vec3( mapN.xy, sqrt( saturate( 1.0 - dot( mapN.xy, mapN.xy ) ) ) );
	#endif
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,BT=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,zT=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,HT=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
		#ifdef FLIP_SIDED
			vBitangent = - vBitangent;
		#endif
	#endif
#endif`,GT=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,VT=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,WT=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,$T=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,XT=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,qT=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,YT=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,KT=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,ZT=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,JT=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,QT=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,jT=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,ew=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,tw=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,nw=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,iw=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	#ifdef HAS_NORMAL
		vec3 shadowWorldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
	#else
		vec3 shadowWorldNormal = vec3( 0.0 );
	#endif
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,rw=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,aw=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,sw=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,ow=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,lw=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,cw=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,uw=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,dw=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,fw=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,hw=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,pw=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,mw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,gw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,_w=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,vw=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const xw=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,bw=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Sw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,yw=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vWorldDirection );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ew=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Mw=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Tw=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,ww=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,Aw=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,Rw=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,Cw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Iw=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Nw=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,Pw=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Lw=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,Dw=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,kw=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Uw=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Ow=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,Fw=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Bw=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,zw=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,Hw=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Gw=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Vw=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,Ww=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$w=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Xw=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,qw=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Yw=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Kw=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Zw=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Jw=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,Qw=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,_t={alphahash_fragment:xM,alphahash_pars_fragment:bM,alphamap_fragment:SM,alphamap_pars_fragment:yM,alphatest_fragment:EM,alphatest_pars_fragment:MM,aomap_fragment:TM,aomap_pars_fragment:wM,batching_pars_vertex:AM,batching_vertex:RM,begin_vertex:CM,beginnormal_vertex:IM,bsdfs:NM,iridescence_fragment:PM,bumpmap_pars_fragment:LM,clipping_planes_fragment:DM,clipping_planes_pars_fragment:kM,clipping_planes_pars_vertex:UM,clipping_planes_vertex:OM,color_fragment:FM,color_pars_fragment:BM,color_pars_vertex:zM,color_vertex:HM,common:GM,cube_uv_reflection_fragment:VM,defaultnormal_vertex:WM,displacementmap_pars_vertex:$M,displacementmap_vertex:XM,emissivemap_fragment:qM,emissivemap_pars_fragment:YM,colorspace_fragment:KM,colorspace_pars_fragment:ZM,envmap_fragment:JM,envmap_common_pars_fragment:QM,envmap_pars_fragment:jM,envmap_pars_vertex:eT,envmap_physical_pars_fragment:dT,envmap_vertex:tT,fog_vertex:nT,fog_pars_vertex:iT,fog_fragment:rT,fog_pars_fragment:aT,gradientmap_pars_fragment:sT,lightmap_pars_fragment:oT,lights_lambert_fragment:lT,lights_lambert_pars_fragment:cT,lights_pars_begin:uT,lights_toon_fragment:fT,lights_toon_pars_fragment:hT,lights_phong_fragment:pT,lights_phong_pars_fragment:mT,lights_physical_fragment:gT,lights_physical_pars_fragment:_T,lights_fragment_begin:vT,lights_fragment_maps:xT,lights_fragment_end:bT,lightprobes_pars_fragment:ST,logdepthbuf_fragment:yT,logdepthbuf_pars_fragment:ET,logdepthbuf_pars_vertex:MT,logdepthbuf_vertex:TT,map_fragment:wT,map_pars_fragment:AT,map_particle_fragment:RT,map_particle_pars_fragment:CT,metalnessmap_fragment:IT,metalnessmap_pars_fragment:NT,morphinstance_vertex:PT,morphcolor_vertex:LT,morphnormal_vertex:DT,morphtarget_pars_vertex:kT,morphtarget_vertex:UT,normal_fragment_begin:OT,normal_fragment_maps:FT,normal_pars_fragment:BT,normal_pars_vertex:zT,normal_vertex:HT,normalmap_pars_fragment:GT,clearcoat_normal_fragment_begin:VT,clearcoat_normal_fragment_maps:WT,clearcoat_pars_fragment:$T,iridescence_pars_fragment:XT,opaque_fragment:qT,packing:YT,premultiplied_alpha_fragment:KT,project_vertex:ZT,dithering_fragment:JT,dithering_pars_fragment:QT,roughnessmap_fragment:jT,roughnessmap_pars_fragment:ew,shadowmap_pars_fragment:tw,shadowmap_pars_vertex:nw,shadowmap_vertex:iw,shadowmask_pars_fragment:rw,skinbase_vertex:aw,skinning_pars_vertex:sw,skinning_vertex:ow,skinnormal_vertex:lw,specularmap_fragment:cw,specularmap_pars_fragment:uw,tonemapping_fragment:dw,tonemapping_pars_fragment:fw,transmission_fragment:hw,transmission_pars_fragment:pw,uv_pars_fragment:mw,uv_pars_vertex:gw,uv_vertex:_w,worldpos_vertex:vw,background_vert:xw,background_frag:bw,backgroundCube_vert:Sw,backgroundCube_frag:yw,cube_vert:Ew,cube_frag:Mw,depth_vert:Tw,depth_frag:ww,distance_vert:Aw,distance_frag:Rw,equirect_vert:Cw,equirect_frag:Iw,linedashed_vert:Nw,linedashed_frag:Pw,meshbasic_vert:Lw,meshbasic_frag:Dw,meshlambert_vert:kw,meshlambert_frag:Uw,meshmatcap_vert:Ow,meshmatcap_frag:Fw,meshnormal_vert:Bw,meshnormal_frag:zw,meshphong_vert:Hw,meshphong_frag:Gw,meshphysical_vert:Vw,meshphysical_frag:Ww,meshtoon_vert:$w,meshtoon_frag:Xw,points_vert:qw,points_frag:Yw,shadow_vert:Kw,shadow_frag:Zw,sprite_vert:Jw,sprite_frag:Qw},Ze={common:{diffuse:{value:new Ct(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ht},alphaMap:{value:null},alphaMapTransform:{value:new ht},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ht}},envmap:{envMap:{value:null},envMapRotation:{value:new ht},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ht}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ht}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ht},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ht},normalScale:{value:new xt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ht},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ht}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ht}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ht}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ct(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null},probesSH:{value:null},probesMin:{value:new ge},probesMax:{value:new ge},probesResolution:{value:new ge}},points:{diffuse:{value:new Ct(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ht},alphaTest:{value:0},uvTransform:{value:new ht}},sprite:{diffuse:{value:new Ct(16777215)},opacity:{value:1},center:{value:new xt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ht},alphaMap:{value:null},alphaMapTransform:{value:new ht},alphaTest:{value:0}}},ri={basic:{uniforms:mn([Ze.common,Ze.specularmap,Ze.envmap,Ze.aomap,Ze.lightmap,Ze.fog]),vertexShader:_t.meshbasic_vert,fragmentShader:_t.meshbasic_frag},lambert:{uniforms:mn([Ze.common,Ze.specularmap,Ze.envmap,Ze.aomap,Ze.lightmap,Ze.emissivemap,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,Ze.fog,Ze.lights,{emissive:{value:new Ct(0)},envMapIntensity:{value:1}}]),vertexShader:_t.meshlambert_vert,fragmentShader:_t.meshlambert_frag},phong:{uniforms:mn([Ze.common,Ze.specularmap,Ze.envmap,Ze.aomap,Ze.lightmap,Ze.emissivemap,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,Ze.fog,Ze.lights,{emissive:{value:new Ct(0)},specular:{value:new Ct(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:_t.meshphong_vert,fragmentShader:_t.meshphong_frag},standard:{uniforms:mn([Ze.common,Ze.envmap,Ze.aomap,Ze.lightmap,Ze.emissivemap,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,Ze.roughnessmap,Ze.metalnessmap,Ze.fog,Ze.lights,{emissive:{value:new Ct(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:_t.meshphysical_vert,fragmentShader:_t.meshphysical_frag},toon:{uniforms:mn([Ze.common,Ze.aomap,Ze.lightmap,Ze.emissivemap,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,Ze.gradientmap,Ze.fog,Ze.lights,{emissive:{value:new Ct(0)}}]),vertexShader:_t.meshtoon_vert,fragmentShader:_t.meshtoon_frag},matcap:{uniforms:mn([Ze.common,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,Ze.fog,{matcap:{value:null}}]),vertexShader:_t.meshmatcap_vert,fragmentShader:_t.meshmatcap_frag},points:{uniforms:mn([Ze.points,Ze.fog]),vertexShader:_t.points_vert,fragmentShader:_t.points_frag},dashed:{uniforms:mn([Ze.common,Ze.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:_t.linedashed_vert,fragmentShader:_t.linedashed_frag},depth:{uniforms:mn([Ze.common,Ze.displacementmap]),vertexShader:_t.depth_vert,fragmentShader:_t.depth_frag},normal:{uniforms:mn([Ze.common,Ze.bumpmap,Ze.normalmap,Ze.displacementmap,{opacity:{value:1}}]),vertexShader:_t.meshnormal_vert,fragmentShader:_t.meshnormal_frag},sprite:{uniforms:mn([Ze.sprite,Ze.fog]),vertexShader:_t.sprite_vert,fragmentShader:_t.sprite_frag},background:{uniforms:{uvTransform:{value:new ht},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:_t.background_vert,fragmentShader:_t.background_frag},backgroundCube:{uniforms:{envMap:{value:null},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ht}},vertexShader:_t.backgroundCube_vert,fragmentShader:_t.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:_t.cube_vert,fragmentShader:_t.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:_t.equirect_vert,fragmentShader:_t.equirect_frag},distance:{uniforms:mn([Ze.common,Ze.displacementmap,{referencePosition:{value:new ge},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:_t.distance_vert,fragmentShader:_t.distance_frag},shadow:{uniforms:mn([Ze.lights,Ze.fog,{color:{value:new Ct(0)},opacity:{value:1}}]),vertexShader:_t.shadow_vert,fragmentShader:_t.shadow_frag}};ri.physical={uniforms:mn([ri.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ht},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ht},clearcoatNormalScale:{value:new xt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ht},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ht},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ht},sheen:{value:0},sheenColor:{value:new Ct(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ht},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ht},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ht},transmissionSamplerSize:{value:new xt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ht},attenuationDistance:{value:0},attenuationColor:{value:new Ct(0)},specularColor:{value:new Ct(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ht},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ht},anisotropyVector:{value:new xt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ht}}]),vertexShader:_t.meshphysical_vert,fragmentShader:_t.meshphysical_frag};const zs={r:0,b:0,g:0},jw=new Xt,Hp=new ht;Hp.set(-1,0,0,0,1,0,0,0,1);function e1(n,e,t,i,r,a){const o=new Ct(0);let l=r===!0?0:1,c,u,f=null,h=0,d=null;function p(O){let D=O.isScene===!0?O.background:null;if(D&&D.isTexture){const y=O.backgroundBlurriness>0;D=e.get(D,y)}return D}function m(O){let D=!1;const y=p(O);y===null?g(o,l):y&&y.isColor&&(g(y,1),D=!0);const B=n.xr.getEnvironmentBlendMode();B==="additive"?t.buffers.color.setClear(0,0,0,1,a):B==="alpha-blend"&&t.buffers.color.setClear(0,0,0,0,a),(n.autoClear||D)&&(t.buffers.depth.setTest(!0),t.buffers.depth.setMask(!0),t.buffers.color.setMask(!0),n.clear(n.autoClearColor,n.autoClearDepth,n.autoClearStencil))}function E(O,D){const y=p(D);y&&(y.isCubeTexture||y.mapping===bo)?(u===void 0&&(u=new gi(new os(1,1,1),new Kn({name:"BackgroundCubeMaterial",uniforms:ca(ri.backgroundCube.uniforms),vertexShader:ri.backgroundCube.vertexShader,fragmentShader:ri.backgroundCube.fragmentShader,side:yn,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(B,R,C){this.matrixWorld.copyPosition(C.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(u)),u.material.uniforms.envMap.value=y,u.material.uniforms.backgroundBlurriness.value=D.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=D.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(jw.makeRotationFromEuler(D.backgroundRotation)).transpose(),y.isCubeTexture&&y.isRenderTargetTexture===!1&&u.material.uniforms.backgroundRotation.value.premultiply(Hp),u.material.toneMapped=bt.getTransfer(y.colorSpace)!==Nt,(f!==y||h!==y.version||d!==n.toneMapping)&&(u.material.needsUpdate=!0,f=y,h=y.version,d=n.toneMapping),u.layers.enableAll(),O.unshift(u,u.geometry,u.material,0,0,null)):y&&y.isTexture&&(c===void 0&&(c=new gi(new yo(2,2),new Kn({name:"BackgroundMaterial",uniforms:ca(ri.background.uniforms),vertexShader:ri.background.vertexShader,fragmentShader:ri.background.fragmentShader,side:ir,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(c)),c.material.uniforms.t2D.value=y,c.material.uniforms.backgroundIntensity.value=D.backgroundIntensity,c.material.toneMapped=bt.getTransfer(y.colorSpace)!==Nt,y.matrixAutoUpdate===!0&&y.updateMatrix(),c.material.uniforms.uvTransform.value.copy(y.matrix),(f!==y||h!==y.version||d!==n.toneMapping)&&(c.material.needsUpdate=!0,f=y,h=y.version,d=n.toneMapping),c.layers.enableAll(),O.unshift(c,c.geometry,c.material,0,0,null))}function g(O,D){O.getRGB(zs,Up(n)),t.buffers.color.setClear(zs.r,zs.g,zs.b,D,a)}function _(){u!==void 0&&(u.geometry.dispose(),u.material.dispose(),u=void 0),c!==void 0&&(c.geometry.dispose(),c.material.dispose(),c=void 0)}return{getClearColor:function(){return o},setClearColor:function(O,D=1){o.set(O),l=D,g(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(O){l=O,g(o,l)},render:m,addToRenderList:E,dispose:_}}function t1(n,e){const t=n.getParameter(n.MAX_VERTEX_ATTRIBS),i={},r=d(null);let a=r,o=!1;function l(z,H,q,Q,G){let T=!1;const w=h(z,Q,q,H);a!==w&&(a=w,u(a.object)),T=p(z,Q,q,G),T&&m(z,Q,q,G),G!==null&&e.update(G,n.ELEMENT_ARRAY_BUFFER),(T||o)&&(o=!1,y(z,H,q,Q),G!==null&&n.bindBuffer(n.ELEMENT_ARRAY_BUFFER,e.get(G).buffer))}function c(){return n.createVertexArray()}function u(z){return n.bindVertexArray(z)}function f(z){return n.deleteVertexArray(z)}function h(z,H,q,Q){const G=Q.wireframe===!0;let T=i[H.id];T===void 0&&(T={},i[H.id]=T);const w=z.isInstancedMesh===!0?z.id:0;let I=T[w];I===void 0&&(I={},T[w]=I);let F=I[q.id];F===void 0&&(F={},I[q.id]=F);let Y=F[G];return Y===void 0&&(Y=d(c()),F[G]=Y),Y}function d(z){const H=[],q=[],Q=[];for(let G=0;G<t;G++)H[G]=0,q[G]=0,Q[G]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:q,attributeDivisors:Q,object:z,attributes:{},index:null}}function p(z,H,q,Q){const G=a.attributes,T=H.attributes;let w=0;const I=q.getAttributes();for(const F in I)if(I[F].location>=0){const te=G[F];let X=T[F];if(X===void 0&&(F==="instanceMatrix"&&z.instanceMatrix&&(X=z.instanceMatrix),F==="instanceColor"&&z.instanceColor&&(X=z.instanceColor)),te===void 0||te.attribute!==X||X&&te.data!==X.data)return!0;w++}return a.attributesNum!==w||a.index!==Q}function m(z,H,q,Q){const G={},T=H.attributes;let w=0;const I=q.getAttributes();for(const F in I)if(I[F].location>=0){let te=T[F];te===void 0&&(F==="instanceMatrix"&&z.instanceMatrix&&(te=z.instanceMatrix),F==="instanceColor"&&z.instanceColor&&(te=z.instanceColor));const X={};X.attribute=te,te&&te.data&&(X.data=te.data),G[F]=X,w++}a.attributes=G,a.attributesNum=w,a.index=Q}function E(){const z=a.newAttributes;for(let H=0,q=z.length;H<q;H++)z[H]=0}function g(z){_(z,0)}function _(z,H){const q=a.newAttributes,Q=a.enabledAttributes,G=a.attributeDivisors;q[z]=1,Q[z]===0&&(n.enableVertexAttribArray(z),Q[z]=1),G[z]!==H&&(n.vertexAttribDivisor(z,H),G[z]=H)}function O(){const z=a.newAttributes,H=a.enabledAttributes;for(let q=0,Q=H.length;q<Q;q++)H[q]!==z[q]&&(n.disableVertexAttribArray(q),H[q]=0)}function D(z,H,q,Q,G,T,w){w===!0?n.vertexAttribIPointer(z,H,q,G,T):n.vertexAttribPointer(z,H,q,Q,G,T)}function y(z,H,q,Q){E();const G=Q.attributes,T=q.getAttributes(),w=H.defaultAttributeValues;for(const I in T){const F=T[I];if(F.location>=0){let Y=G[I];if(Y===void 0&&(I==="instanceMatrix"&&z.instanceMatrix&&(Y=z.instanceMatrix),I==="instanceColor"&&z.instanceColor&&(Y=z.instanceColor)),Y!==void 0){const te=Y.normalized,X=Y.itemSize,K=e.get(Y);if(K===void 0)continue;const se=K.buffer,ne=K.type,N=K.bytesPerElement,V=ne===n.INT||ne===n.UNSIGNED_INT||Y.gpuType===pu;if(Y.isInterleavedBufferAttribute){const re=Y.data,Me=re.stride,fe=Y.offset;if(re.isInstancedInterleavedBuffer){for(let oe=0;oe<F.locationSize;oe++)_(F.location+oe,re.meshPerAttribute);z.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=re.meshPerAttribute*re.count)}else for(let oe=0;oe<F.locationSize;oe++)g(F.location+oe);n.bindBuffer(n.ARRAY_BUFFER,se);for(let oe=0;oe<F.locationSize;oe++)D(F.location+oe,X/F.locationSize,ne,te,Me*N,(fe+X/F.locationSize*oe)*N,V)}else{if(Y.isInstancedBufferAttribute){for(let re=0;re<F.locationSize;re++)_(F.location+re,Y.meshPerAttribute);z.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=Y.meshPerAttribute*Y.count)}else for(let re=0;re<F.locationSize;re++)g(F.location+re);n.bindBuffer(n.ARRAY_BUFFER,se);for(let re=0;re<F.locationSize;re++)D(F.location+re,X/F.locationSize,ne,te,X*N,X/F.locationSize*re*N,V)}}else if(w!==void 0){const te=w[I];if(te!==void 0)switch(te.length){case 2:n.vertexAttrib2fv(F.location,te);break;case 3:n.vertexAttrib3fv(F.location,te);break;case 4:n.vertexAttrib4fv(F.location,te);break;default:n.vertexAttrib1fv(F.location,te)}}}}O()}function B(){A();for(const z in i){const H=i[z];for(const q in H){const Q=H[q];for(const G in Q){const T=Q[G];for(const w in T)f(T[w].object),delete T[w];delete Q[G]}}delete i[z]}}function R(z){if(i[z.id]===void 0)return;const H=i[z.id];for(const q in H){const Q=H[q];for(const G in Q){const T=Q[G];for(const w in T)f(T[w].object),delete T[w];delete Q[G]}}delete i[z.id]}function C(z){for(const H in i){const q=i[H];for(const Q in q){const G=q[Q];if(G[z.id]===void 0)continue;const T=G[z.id];for(const w in T)f(T[w].object),delete T[w];delete G[z.id]}}}function b(z){for(const H in i){const q=i[H],Q=z.isInstancedMesh===!0?z.id:0,G=q[Q];if(G!==void 0){for(const T in G){const w=G[T];for(const I in w)f(w[I].object),delete w[I];delete G[T]}delete q[Q],Object.keys(q).length===0&&delete i[H]}}}function A(){k(),o=!0,a!==r&&(a=r,u(a.object))}function k(){r.geometry=null,r.program=null,r.wireframe=!1}return{setup:l,reset:A,resetDefaultState:k,dispose:B,releaseStatesOfGeometry:R,releaseStatesOfObject:b,releaseStatesOfProgram:C,initAttributes:E,enableAttribute:g,disableUnusedAttributes:O}}function n1(n,e,t){let i;function r(c){i=c}function a(c,u){n.drawArrays(i,c,u),t.update(u,i,1)}function o(c,u,f){f!==0&&(n.drawArraysInstanced(i,c,u,f),t.update(u,i,f))}function l(c,u,f){if(f===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(i,c,0,u,0,f);let d=0;for(let p=0;p<f;p++)d+=u[p];t.update(d,i,1)}this.setMode=r,this.render=a,this.renderInstances=o,this.renderMultiDraw=l}function i1(n,e,t,i){let r;function a(){if(r!==void 0)return r;if(e.has("EXT_texture_filter_anisotropic")===!0){const C=e.get("EXT_texture_filter_anisotropic");r=n.getParameter(C.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else r=0;return r}function o(C){return!(C!==Xn&&i.convert(C)!==n.getParameter(n.IMPLEMENTATION_COLOR_READ_FORMAT))}function l(C){const b=C===ki&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(C!==In&&i.convert(C)!==n.getParameter(n.IMPLEMENTATION_COLOR_READ_TYPE)&&C!==ci&&!b)}function c(C){if(C==="highp"){if(n.getShaderPrecisionFormat(n.VERTEX_SHADER,n.HIGH_FLOAT).precision>0&&n.getShaderPrecisionFormat(n.FRAGMENT_SHADER,n.HIGH_FLOAT).precision>0)return"highp";C="mediump"}return C==="mediump"&&n.getShaderPrecisionFormat(n.VERTEX_SHADER,n.MEDIUM_FLOAT).precision>0&&n.getShaderPrecisionFormat(n.FRAGMENT_SHADER,n.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let u=t.precision!==void 0?t.precision:"highp";const f=c(u);f!==u&&(ut("WebGLRenderer:",u,"not supported, using",f,"instead."),u=f);const h=t.logarithmicDepthBuffer===!0,d=t.reversedDepthBuffer===!0&&e.has("EXT_clip_control");t.reversedDepthBuffer===!0&&d===!1&&ut("WebGLRenderer: Unable to use reversed depth buffer due to missing EXT_clip_control extension. Fallback to default depth buffer.");const p=n.getParameter(n.MAX_TEXTURE_IMAGE_UNITS),m=n.getParameter(n.MAX_VERTEX_TEXTURE_IMAGE_UNITS),E=n.getParameter(n.MAX_TEXTURE_SIZE),g=n.getParameter(n.MAX_CUBE_MAP_TEXTURE_SIZE),_=n.getParameter(n.MAX_VERTEX_ATTRIBS),O=n.getParameter(n.MAX_VERTEX_UNIFORM_VECTORS),D=n.getParameter(n.MAX_VARYING_VECTORS),y=n.getParameter(n.MAX_FRAGMENT_UNIFORM_VECTORS),B=n.getParameter(n.MAX_SAMPLES),R=n.getParameter(n.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:a,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:l,precision:u,logarithmicDepthBuffer:h,reversedDepthBuffer:d,maxTextures:p,maxVertexTextures:m,maxTextureSize:E,maxCubemapSize:g,maxAttributes:_,maxVertexUniforms:O,maxVaryings:D,maxFragmentUniforms:y,maxSamples:B,samples:R}}function r1(n){const e=this;let t=null,i=0,r=!1,a=!1;const o=new ur,l=new ht,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(h,d){const p=h.length!==0||d||i!==0||r;return r=d,i=h.length,p},this.beginShadows=function(){a=!0,f(null)},this.endShadows=function(){a=!1},this.setGlobalState=function(h,d){t=f(h,d,0)},this.setState=function(h,d,p){const m=h.clippingPlanes,E=h.clipIntersection,g=h.clipShadows,_=n.get(h);if(!r||m===null||m.length===0||a&&!g)a?f(null):u();else{const O=a?0:i,D=O*4;let y=_.clippingState||null;c.value=y,y=f(m,d,D,p);for(let B=0;B!==D;++B)y[B]=t[B];_.clippingState=y,this.numIntersection=E?this.numPlanes:0,this.numPlanes+=O}};function u(){c.value!==t&&(c.value=t,c.needsUpdate=i>0),e.numPlanes=i,e.numIntersection=0}function f(h,d,p,m){const E=h!==null?h.length:0;let g=null;if(E!==0){if(g=c.value,m!==!0||g===null){const _=p+E*4,O=d.matrixWorldInverse;l.getNormalMatrix(O),(g===null||g.length<_)&&(g=new Float32Array(_));for(let D=0,y=p;D!==E;++D,y+=4)o.copy(h[D]).applyMatrix4(O,l),o.normal.toArray(g,y),g[y+3]=o.constant}c.value=g,c.needsUpdate=!0}return e.numPlanes=E,e.numIntersection=0,g}}const ji=4,gf=[.125,.215,.35,.446,.526,.582],hr=20,a1=256,Ia=new Bp,_f=new Ct;let pl=null,ml=0,gl=0,_l=!1;const s1=new ge;class vf{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(e,t=0,i=.1,r=100,a={}){const{size:o=256,position:l=s1}=a;pl=this._renderer.getRenderTarget(),ml=this._renderer.getActiveCubeFace(),gl=this._renderer.getActiveMipmapLevel(),_l=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(o);const c=this._allocateTargets();return c.depthBuffer=!0,this._sceneToCubeUV(e,i,r,c,l),t>0&&this._blur(c,0,0,t),this._applyPMREM(c),this._cleanup(c),c}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Sf(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=bf(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodMeshes.length;e++)this._lodMeshes[e].geometry.dispose()}_cleanup(e){this._renderer.setRenderTarget(pl,ml,gl),this._renderer.xr.enabled=_l,e.scissorTest=!1,Zr(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===br||e.mapping===oa?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),pl=this._renderer.getRenderTarget(),ml=this._renderer.getActiveCubeFace(),gl=this._renderer.getActiveMipmapLevel(),_l=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const i=t||this._allocateTargets();return this._textureToCubeUV(e,i),this._applyPMREM(i),this._cleanup(i),i}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,i={magFilter:fn,minFilter:fn,generateMipmaps:!1,type:ki,format:Xn,colorSpace:oo,depthBuffer:!1},r=xf(e,t,i);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=xf(e,t,i);const{_lodMax:a}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=o1(a)),this._blurMaterial=c1(a,e,t),this._ggxMaterial=l1(a,e,t)}return r}_compileMaterial(e){const t=new gi(new vi,e);this._renderer.compile(t,Ia)}_sceneToCubeUV(e,t,i,r,a){const c=new Cn(90,1,t,i),u=[1,-1,1,1,1,1],f=[1,1,1,-1,-1,-1],h=this._renderer,d=h.autoClear,p=h.toneMapping;h.getClearColor(_f),h.toneMapping=di,h.autoClear=!1,h.state.buffers.depth.getReversed()&&(h.setRenderTarget(r),h.clearDepth(),h.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new gi(new os,new Lp({name:"PMREM.Background",side:yn,depthWrite:!1,depthTest:!1})));const E=this._backgroundBox,g=E.material;let _=!1;const O=e.background;O?O.isColor&&(g.color.copy(O),e.background=null,_=!0):(g.color.copy(_f),_=!0);for(let D=0;D<6;D++){const y=D%3;y===0?(c.up.set(0,u[D],0),c.position.set(a.x,a.y,a.z),c.lookAt(a.x+f[D],a.y,a.z)):y===1?(c.up.set(0,0,u[D]),c.position.set(a.x,a.y,a.z),c.lookAt(a.x,a.y+f[D],a.z)):(c.up.set(0,u[D],0),c.position.set(a.x,a.y,a.z),c.lookAt(a.x,a.y,a.z+f[D]));const B=this._cubeSize;Zr(r,y*B,D>2?B:0,B,B),h.setRenderTarget(r),_&&h.render(E,c),h.render(e,c)}h.toneMapping=p,h.autoClear=d,e.background=O}_textureToCubeUV(e,t){const i=this._renderer,r=e.mapping===br||e.mapping===oa;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=Sf()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=bf());const a=r?this._cubemapMaterial:this._equirectMaterial,o=this._lodMeshes[0];o.material=a;const l=a.uniforms;l.envMap.value=e;const c=this._cubeSize;Zr(t,0,0,3*c,2*c),i.setRenderTarget(t),i.render(o,Ia)}_applyPMREM(e){const t=this._renderer,i=t.autoClear;t.autoClear=!1;const r=this._lodMeshes.length;for(let a=1;a<r;a++)this._applyGGXFilter(e,a-1,a);t.autoClear=i}_applyGGXFilter(e,t,i){const r=this._renderer,a=this._pingPongRenderTarget,o=this._ggxMaterial,l=this._lodMeshes[i];l.material=o;const c=o.uniforms,u=i/(this._lodMeshes.length-1),f=t/(this._lodMeshes.length-1),h=Math.sqrt(u*u-f*f),d=0+u*1.25,p=h*d,{_lodMax:m}=this,E=this._sizeLods[i],g=3*E*(i>m-ji?i-m+ji:0),_=4*(this._cubeSize-E);c.envMap.value=e.texture,c.roughness.value=p,c.mipInt.value=m-t,Zr(a,g,_,3*E,2*E),r.setRenderTarget(a),r.render(l,Ia),c.envMap.value=a.texture,c.roughness.value=0,c.mipInt.value=m-i,Zr(e,g,_,3*E,2*E),r.setRenderTarget(e),r.render(l,Ia)}_blur(e,t,i,r,a){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,i,r,"latitudinal",a),this._halfBlur(o,e,i,i,r,"longitudinal",a)}_halfBlur(e,t,i,r,a,o,l){const c=this._renderer,u=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&Rt("blur direction must be either latitudinal or longitudinal!");const f=3,h=this._lodMeshes[r];h.material=u;const d=u.uniforms,p=this._sizeLods[i]-1,m=isFinite(a)?Math.PI/(2*p):2*Math.PI/(2*hr-1),E=a/m,g=isFinite(a)?1+Math.floor(f*E):hr;g>hr&&ut(`sigmaRadians, ${a}, is too large and will clip, as it requested ${g} samples when the maximum is set to ${hr}`);const _=[];let O=0;for(let C=0;C<hr;++C){const b=C/E,A=Math.exp(-b*b/2);_.push(A),C===0?O+=A:C<g&&(O+=2*A)}for(let C=0;C<_.length;C++)_[C]=_[C]/O;d.envMap.value=e.texture,d.samples.value=g,d.weights.value=_,d.latitudinal.value=o==="latitudinal",l&&(d.poleAxis.value=l);const{_lodMax:D}=this;d.dTheta.value=m,d.mipInt.value=D-i;const y=this._sizeLods[r],B=3*y*(r>D-ji?r-D+ji:0),R=4*(this._cubeSize-y);Zr(t,B,R,3*y,2*y),c.setRenderTarget(t),c.render(h,Ia)}}function o1(n){const e=[],t=[],i=[];let r=n;const a=n-ji+1+gf.length;for(let o=0;o<a;o++){const l=Math.pow(2,r);e.push(l);let c=1/l;o>n-ji?c=gf[o-n+ji-1]:o===0&&(c=0),t.push(c);const u=1/(l-2),f=-u,h=1+u,d=[f,f,h,f,h,h,f,f,h,h,f,h],p=6,m=6,E=3,g=2,_=1,O=new Float32Array(E*m*p),D=new Float32Array(g*m*p),y=new Float32Array(_*m*p);for(let R=0;R<p;R++){const C=R%3*2/3-1,b=R>2?0:-1,A=[C,b,0,C+2/3,b,0,C+2/3,b+1,0,C,b,0,C+2/3,b+1,0,C,b+1,0];O.set(A,E*m*R),D.set(d,g*m*R);const k=[R,R,R,R,R,R];y.set(k,_*m*R)}const B=new vi;B.setAttribute("position",new hi(O,E)),B.setAttribute("uv",new hi(D,g)),B.setAttribute("faceIndex",new hi(y,_)),i.push(new gi(B,null)),r>ji&&r--}return{lodMeshes:i,sizeLods:e,sigmas:t}}function xf(n,e,t){const i=new fi(n,e,t);return i.texture.mapping=bo,i.texture.name="PMREM.cubeUv",i.scissorTest=!0,i}function Zr(n,e,t,i,r){n.viewport.set(e,t,i,r),n.scissor.set(e,t,i,r)}function l1(n,e,t){return new Kn({name:"PMREMGGXConvolution",defines:{GGX_SAMPLES:a1,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${n}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:Eo(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:Ri,depthTest:!1,depthWrite:!1})}function c1(n,e,t){const i=new Float32Array(hr),r=new ge(0,1,0);return new Kn({name:"SphericalGaussianBlur",defines:{n:hr,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${n}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:i},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:Eo(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Ri,depthTest:!1,depthWrite:!1})}function bf(){return new Kn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Eo(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Ri,depthTest:!1,depthWrite:!1})}function Sf(){return new Kn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Eo(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Ri,depthTest:!1,depthWrite:!1})}function Eo(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}class Gp extends fi{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const i={width:e,height:e,depth:1},r=[i,i,i,i,i,i];this.texture=new Dp(r),this._setTextureOptions(t),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const i={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new os(5,5,5),a=new Kn({name:"CubemapFromEquirect",uniforms:ca(i.uniforms),vertexShader:i.vertexShader,fragmentShader:i.fragmentShader,side:yn,blending:Ri});a.uniforms.tEquirect.value=t;const o=new gi(r,a),l=t.minFilter;return t.minFilter===pr&&(t.minFilter=fn),new mM(1,10,this).update(e,o),t.minFilter=l,o.geometry.dispose(),o.material.dispose(),this}clear(e,t=!0,i=!0,r=!0){const a=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,i,r);e.setRenderTarget(a)}}function u1(n){let e=new WeakMap,t=new WeakMap,i=null;function r(d,p=!1){return d==null?null:p?o(d):a(d)}function a(d){if(d&&d.isTexture){const p=d.mapping;if(p===zo||p===Ho)if(e.has(d)){const m=e.get(d).texture;return l(m,d.mapping)}else{const m=d.image;if(m&&m.height>0){const E=new Gp(m.height);return E.fromEquirectangularTexture(n,d),e.set(d,E),d.addEventListener("dispose",u),l(E.texture,d.mapping)}else return null}}return d}function o(d){if(d&&d.isTexture){const p=d.mapping,m=p===zo||p===Ho,E=p===br||p===oa;if(m||E){let g=t.get(d);const _=g!==void 0?g.texture.pmremVersion:0;if(d.isRenderTargetTexture&&d.pmremVersion!==_)return i===null&&(i=new vf(n)),g=m?i.fromEquirectangular(d,g):i.fromCubemap(d,g),g.texture.pmremVersion=d.pmremVersion,t.set(d,g),g.texture;if(g!==void 0)return g.texture;{const O=d.image;return m&&O&&O.height>0||E&&O&&c(O)?(i===null&&(i=new vf(n)),g=m?i.fromEquirectangular(d):i.fromCubemap(d),g.texture.pmremVersion=d.pmremVersion,t.set(d,g),d.addEventListener("dispose",f),g.texture):null}}}return d}function l(d,p){return p===zo?d.mapping=br:p===Ho&&(d.mapping=oa),d}function c(d){let p=0;const m=6;for(let E=0;E<m;E++)d[E]!==void 0&&p++;return p===m}function u(d){const p=d.target;p.removeEventListener("dispose",u);const m=e.get(p);m!==void 0&&(e.delete(p),m.dispose())}function f(d){const p=d.target;p.removeEventListener("dispose",f);const m=t.get(p);m!==void 0&&(t.delete(p),m.dispose())}function h(){e=new WeakMap,t=new WeakMap,i!==null&&(i.dispose(),i=null)}return{get:r,dispose:h}}function d1(n){const e={};function t(i){if(e[i]!==void 0)return e[i];const r=n.getExtension(i);return e[i]=r,r}return{has:function(i){return t(i)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(i){const r=t(i);return r===null&&ia("WebGLRenderer: "+i+" extension not supported."),r}}}function f1(n,e,t,i){const r={},a=new WeakMap;function o(h){const d=h.target;d.index!==null&&e.remove(d.index);for(const m in d.attributes)e.remove(d.attributes[m]);d.removeEventListener("dispose",o),delete r[d.id];const p=a.get(d);p&&(e.remove(p),a.delete(d)),i.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function l(h,d){return r[d.id]===!0||(d.addEventListener("dispose",o),r[d.id]=!0,t.memory.geometries++),d}function c(h){const d=h.attributes;for(const p in d)e.update(d[p],n.ARRAY_BUFFER)}function u(h){const d=[],p=h.index,m=h.attributes.position;let E=0;if(m===void 0)return;if(p!==null){const O=p.array;E=p.version;for(let D=0,y=O.length;D<y;D+=3){const B=O[D+0],R=O[D+1],C=O[D+2];d.push(B,R,R,C,C,B)}}else{const O=m.array;E=m.version;for(let D=0,y=O.length/3-1;D<y;D+=3){const B=D+0,R=D+1,C=D+2;d.push(B,R,R,C,C,B)}}const g=new(m.count>=65535?Pp:Np)(d,1);g.version=E;const _=a.get(h);_&&e.remove(_),a.set(h,g)}function f(h){const d=a.get(h);if(d){const p=h.index;p!==null&&d.version<p.version&&u(h)}else u(h);return a.get(h)}return{get:l,update:c,getWireframeAttribute:f}}function h1(n,e,t){let i;function r(h){i=h}let a,o;function l(h){a=h.type,o=h.bytesPerElement}function c(h,d){n.drawElements(i,d,a,h*o),t.update(d,i,1)}function u(h,d,p){p!==0&&(n.drawElementsInstanced(i,d,a,h*o,p),t.update(d,i,p))}function f(h,d,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(i,d,0,a,h,0,p);let E=0;for(let g=0;g<p;g++)E+=d[g];t.update(E,i,1)}this.setMode=r,this.setIndex=l,this.render=c,this.renderInstances=u,this.renderMultiDraw=f}function p1(n){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function i(a,o,l){switch(t.calls++,o){case n.TRIANGLES:t.triangles+=l*(a/3);break;case n.LINES:t.lines+=l*(a/2);break;case n.LINE_STRIP:t.lines+=l*(a-1);break;case n.LINE_LOOP:t.lines+=l*a;break;case n.POINTS:t.points+=l*a;break;default:Rt("WebGLInfo: Unknown draw mode:",o);break}}function r(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:r,update:i}}function m1(n,e,t){const i=new WeakMap,r=new Gt;function a(o,l,c){const u=o.morphTargetInfluences,f=l.morphAttributes.position||l.morphAttributes.normal||l.morphAttributes.color,h=f!==void 0?f.length:0;let d=i.get(l);if(d===void 0||d.count!==h){let A=function(){C.dispose(),i.delete(l),l.removeEventListener("dispose",A)};d!==void 0&&d.texture.dispose();const p=l.morphAttributes.position!==void 0,m=l.morphAttributes.normal!==void 0,E=l.morphAttributes.color!==void 0,g=l.morphAttributes.position||[],_=l.morphAttributes.normal||[],O=l.morphAttributes.color||[];let D=0;p===!0&&(D=1),m===!0&&(D=2),E===!0&&(D=3);let y=l.attributes.position.count*D,B=1;y>e.maxTextureSize&&(B=Math.ceil(y/e.maxTextureSize),y=e.maxTextureSize);const R=new Float32Array(y*B*4*h),C=new Rp(R,y,B,h);C.type=ci,C.needsUpdate=!0;const b=D*4;for(let k=0;k<h;k++){const z=g[k],H=_[k],q=O[k],Q=y*B*4*k;for(let G=0;G<z.count;G++){const T=G*b;p===!0&&(r.fromBufferAttribute(z,G),R[Q+T+0]=r.x,R[Q+T+1]=r.y,R[Q+T+2]=r.z,R[Q+T+3]=0),m===!0&&(r.fromBufferAttribute(H,G),R[Q+T+4]=r.x,R[Q+T+5]=r.y,R[Q+T+6]=r.z,R[Q+T+7]=0),E===!0&&(r.fromBufferAttribute(q,G),R[Q+T+8]=r.x,R[Q+T+9]=r.y,R[Q+T+10]=r.z,R[Q+T+11]=q.itemSize===4?r.w:1)}}d={count:h,texture:C,size:new xt(y,B)},i.set(l,d),l.addEventListener("dispose",A)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)c.getUniforms().setValue(n,"morphTexture",o.morphTexture,t);else{let p=0;for(let E=0;E<u.length;E++)p+=u[E];const m=l.morphTargetsRelative?1:1-p;c.getUniforms().setValue(n,"morphTargetBaseInfluence",m),c.getUniforms().setValue(n,"morphTargetInfluences",u)}c.getUniforms().setValue(n,"morphTargetsTexture",d.texture,t),c.getUniforms().setValue(n,"morphTargetsTextureSize",d.size)}return{update:a}}function g1(n,e,t,i,r){let a=new WeakMap;function o(u){const f=r.render.frame,h=u.geometry,d=e.get(u,h);if(a.get(d)!==f&&(e.update(d),a.set(d,f)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),a.get(u)!==f&&(t.update(u.instanceMatrix,n.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,n.ARRAY_BUFFER),a.set(u,f))),u.isSkinnedMesh){const p=u.skeleton;a.get(p)!==f&&(p.update(),a.set(p,f))}return d}function l(){a=new WeakMap}function c(u){const f=u.target;f.removeEventListener("dispose",c),i.releaseStatesOfObject(f),t.remove(f.instanceMatrix),f.instanceColor!==null&&t.remove(f.instanceColor)}return{update:o,dispose:l}}const _1={[hp]:"LINEAR_TONE_MAPPING",[pp]:"REINHARD_TONE_MAPPING",[mp]:"CINEON_TONE_MAPPING",[hu]:"ACES_FILMIC_TONE_MAPPING",[_p]:"AGX_TONE_MAPPING",[vp]:"NEUTRAL_TONE_MAPPING",[gp]:"CUSTOM_TONE_MAPPING"};function v1(n,e,t,i,r,a){const o=new fi(e,t,{type:n,depthBuffer:r,stencilBuffer:a,samples:i?4:0,depthTexture:r?new la(e,t):void 0}),l=new fi(e,t,{type:ki,depthBuffer:!1,stencilBuffer:!1}),c=new vi;c.setAttribute("position",new Dn([-1,3,0,-1,-1,0,3,-1,0],3)),c.setAttribute("uv",new Dn([0,2,0,0,2,0],2));const u=new cM({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),f=new gi(c,u),h=new Bp(-1,1,1,-1,0,1);let d=null,p=null,m=!1,E,g=null,_=[],O=!1;this.setSize=function(D,y){o.setSize(D,y),l.setSize(D,y);for(let B=0;B<_.length;B++){const R=_[B];R.setSize&&R.setSize(D,y)}},this.setEffects=function(D){_=D,O=_.length>0&&_[0].isRenderPass===!0;const y=o.width,B=o.height;for(let R=0;R<_.length;R++){const C=_[R];C.setSize&&C.setSize(y,B)}},this.begin=function(D,y){if(m||D.toneMapping===di&&_.length===0)return!1;if(g=y,y!==null){const B=y.width,R=y.height;(o.width!==B||o.height!==R)&&this.setSize(B,R)}return O===!1&&D.setRenderTarget(o),E=D.toneMapping,D.toneMapping=di,!0},this.hasRenderPass=function(){return O},this.end=function(D,y){D.toneMapping=E,m=!0;let B=o,R=l;for(let C=0;C<_.length;C++){const b=_[C];if(b.enabled!==!1&&(b.render(D,R,B,y),b.needsSwap!==!1)){const A=B;B=R,R=A}}if(d!==D.outputColorSpace||p!==D.toneMapping){d=D.outputColorSpace,p=D.toneMapping,u.defines={},bt.getTransfer(d)===Nt&&(u.defines.SRGB_TRANSFER="");const C=_1[p];C&&(u.defines[C]=""),u.needsUpdate=!0}u.uniforms.tDiffuse.value=B.texture,D.setRenderTarget(g),D.render(f,h),g=null,m=!1},this.isCompositing=function(){return m},this.dispose=function(){o.depthTexture&&o.depthTexture.dispose(),o.dispose(),l.dispose(),c.dispose(),u.dispose()}}const Vp=new _n,bc=new la(1,1),Wp=new Rp,$p=new BE,Xp=new Dp,yf=[],Ef=[],Mf=new Float32Array(16),Tf=new Float32Array(9),wf=new Float32Array(4);function pa(n,e,t){const i=n[0];if(i<=0||i>0)return n;const r=e*t;let a=yf[r];if(a===void 0&&(a=new Float32Array(r),yf[r]=a),e!==0){i.toArray(a,0);for(let o=1,l=0;o!==e;++o)l+=t,n[o].toArray(a,l)}return a}function Qt(n,e){if(n.length!==e.length)return!1;for(let t=0,i=n.length;t<i;t++)if(n[t]!==e[t])return!1;return!0}function jt(n,e){for(let t=0,i=e.length;t<i;t++)n[t]=e[t]}function Mo(n,e){let t=Ef[e];t===void 0&&(t=new Int32Array(e),Ef[e]=t);for(let i=0;i!==e;++i)t[i]=n.allocateTextureUnit();return t}function x1(n,e){const t=this.cache;t[0]!==e&&(n.uniform1f(this.addr,e),t[0]=e)}function b1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Qt(t,e))return;n.uniform2fv(this.addr,e),jt(t,e)}}function S1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(n.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Qt(t,e))return;n.uniform3fv(this.addr,e),jt(t,e)}}function y1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Qt(t,e))return;n.uniform4fv(this.addr,e),jt(t,e)}}function E1(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Qt(t,e))return;n.uniformMatrix2fv(this.addr,!1,e),jt(t,e)}else{if(Qt(t,i))return;wf.set(i),n.uniformMatrix2fv(this.addr,!1,wf),jt(t,i)}}function M1(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Qt(t,e))return;n.uniformMatrix3fv(this.addr,!1,e),jt(t,e)}else{if(Qt(t,i))return;Tf.set(i),n.uniformMatrix3fv(this.addr,!1,Tf),jt(t,i)}}function T1(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Qt(t,e))return;n.uniformMatrix4fv(this.addr,!1,e),jt(t,e)}else{if(Qt(t,i))return;Mf.set(i),n.uniformMatrix4fv(this.addr,!1,Mf),jt(t,i)}}function w1(n,e){const t=this.cache;t[0]!==e&&(n.uniform1i(this.addr,e),t[0]=e)}function A1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Qt(t,e))return;n.uniform2iv(this.addr,e),jt(t,e)}}function R1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Qt(t,e))return;n.uniform3iv(this.addr,e),jt(t,e)}}function C1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Qt(t,e))return;n.uniform4iv(this.addr,e),jt(t,e)}}function I1(n,e){const t=this.cache;t[0]!==e&&(n.uniform1ui(this.addr,e),t[0]=e)}function N1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Qt(t,e))return;n.uniform2uiv(this.addr,e),jt(t,e)}}function P1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Qt(t,e))return;n.uniform3uiv(this.addr,e),jt(t,e)}}function L1(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Qt(t,e))return;n.uniform4uiv(this.addr,e),jt(t,e)}}function D1(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r);let a;this.type===n.SAMPLER_2D_SHADOW?(bc.compareFunction=t.isReversedDepthBuffer()?Su:bu,a=bc):a=Vp,t.setTexture2D(e||a,r)}function k1(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTexture3D(e||$p,r)}function U1(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTextureCube(e||Xp,r)}function O1(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTexture2DArray(e||Wp,r)}function F1(n){switch(n){case 5126:return x1;case 35664:return b1;case 35665:return S1;case 35666:return y1;case 35674:return E1;case 35675:return M1;case 35676:return T1;case 5124:case 35670:return w1;case 35667:case 35671:return A1;case 35668:case 35672:return R1;case 35669:case 35673:return C1;case 5125:return I1;case 36294:return N1;case 36295:return P1;case 36296:return L1;case 35678:case 36198:case 36298:case 36306:case 35682:return D1;case 35679:case 36299:case 36307:return k1;case 35680:case 36300:case 36308:case 36293:return U1;case 36289:case 36303:case 36311:case 36292:return O1}}function B1(n,e){n.uniform1fv(this.addr,e)}function z1(n,e){const t=pa(e,this.size,2);n.uniform2fv(this.addr,t)}function H1(n,e){const t=pa(e,this.size,3);n.uniform3fv(this.addr,t)}function G1(n,e){const t=pa(e,this.size,4);n.uniform4fv(this.addr,t)}function V1(n,e){const t=pa(e,this.size,4);n.uniformMatrix2fv(this.addr,!1,t)}function W1(n,e){const t=pa(e,this.size,9);n.uniformMatrix3fv(this.addr,!1,t)}function $1(n,e){const t=pa(e,this.size,16);n.uniformMatrix4fv(this.addr,!1,t)}function X1(n,e){n.uniform1iv(this.addr,e)}function q1(n,e){n.uniform2iv(this.addr,e)}function Y1(n,e){n.uniform3iv(this.addr,e)}function K1(n,e){n.uniform4iv(this.addr,e)}function Z1(n,e){n.uniform1uiv(this.addr,e)}function J1(n,e){n.uniform2uiv(this.addr,e)}function Q1(n,e){n.uniform3uiv(this.addr,e)}function j1(n,e){n.uniform4uiv(this.addr,e)}function eA(n,e,t){const i=this.cache,r=e.length,a=Mo(t,r);Qt(i,a)||(n.uniform1iv(this.addr,a),jt(i,a));let o;this.type===n.SAMPLER_2D_SHADOW?o=bc:o=Vp;for(let l=0;l!==r;++l)t.setTexture2D(e[l]||o,a[l])}function tA(n,e,t){const i=this.cache,r=e.length,a=Mo(t,r);Qt(i,a)||(n.uniform1iv(this.addr,a),jt(i,a));for(let o=0;o!==r;++o)t.setTexture3D(e[o]||$p,a[o])}function nA(n,e,t){const i=this.cache,r=e.length,a=Mo(t,r);Qt(i,a)||(n.uniform1iv(this.addr,a),jt(i,a));for(let o=0;o!==r;++o)t.setTextureCube(e[o]||Xp,a[o])}function iA(n,e,t){const i=this.cache,r=e.length,a=Mo(t,r);Qt(i,a)||(n.uniform1iv(this.addr,a),jt(i,a));for(let o=0;o!==r;++o)t.setTexture2DArray(e[o]||Wp,a[o])}function rA(n){switch(n){case 5126:return B1;case 35664:return z1;case 35665:return H1;case 35666:return G1;case 35674:return V1;case 35675:return W1;case 35676:return $1;case 5124:case 35670:return X1;case 35667:case 35671:return q1;case 35668:case 35672:return Y1;case 35669:case 35673:return K1;case 5125:return Z1;case 36294:return J1;case 36295:return Q1;case 36296:return j1;case 35678:case 36198:case 36298:case 36306:case 35682:return eA;case 35679:case 36299:case 36307:return tA;case 35680:case 36300:case 36308:case 36293:return nA;case 36289:case 36303:case 36311:case 36292:return iA}}class aA{constructor(e,t,i){this.id=e,this.addr=i,this.cache=[],this.type=t.type,this.setValue=F1(t.type)}}class sA{constructor(e,t,i){this.id=e,this.addr=i,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=rA(t.type)}}class oA{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,i){const r=this.seq;for(let a=0,o=r.length;a!==o;++a){const l=r[a];l.setValue(e,t[l.id],i)}}}const vl=/(\w+)(\])?(\[|\.)?/g;function Af(n,e){n.seq.push(e),n.map[e.id]=e}function lA(n,e,t){const i=n.name,r=i.length;for(vl.lastIndex=0;;){const a=vl.exec(i),o=vl.lastIndex;let l=a[1];const c=a[2]==="]",u=a[3];if(c&&(l=l|0),u===void 0||u==="["&&o+2===r){Af(t,u===void 0?new aA(l,n,e):new sA(l,n,e));break}else{let h=t.map[l];h===void 0&&(h=new oA(l),Af(t,h)),t=h}}}class Ys{constructor(e,t){this.seq=[],this.map={};const i=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let o=0;o<i;++o){const l=e.getActiveUniform(t,o),c=e.getUniformLocation(t,l.name);lA(l,c,this)}const r=[],a=[];for(const o of this.seq)o.type===e.SAMPLER_2D_SHADOW||o.type===e.SAMPLER_CUBE_SHADOW||o.type===e.SAMPLER_2D_ARRAY_SHADOW?r.push(o):a.push(o);r.length>0&&(this.seq=r.concat(a))}setValue(e,t,i,r){const a=this.map[t];a!==void 0&&a.setValue(e,i,r)}setOptional(e,t,i){const r=t[i];r!==void 0&&this.setValue(e,i,r)}static upload(e,t,i,r){for(let a=0,o=t.length;a!==o;++a){const l=t[a],c=i[l.id];c.needsUpdate!==!1&&l.setValue(e,c.value,r)}}static seqWithValue(e,t){const i=[];for(let r=0,a=e.length;r!==a;++r){const o=e[r];o.id in t&&i.push(o)}return i}}function Rf(n,e,t){const i=n.createShader(e);return n.shaderSource(i,t),n.compileShader(i),i}const cA=37297;let uA=0;function dA(n,e){const t=n.split(`
`),i=[],r=Math.max(e-6,0),a=Math.min(e+6,t.length);for(let o=r;o<a;o++){const l=o+1;i.push(`${l===e?">":" "} ${l}: ${t[o]}`)}return i.join(`
`)}const Cf=new ht;function fA(n){bt._getMatrix(Cf,bt.workingColorSpace,n);const e=`mat3( ${Cf.elements.map(t=>t.toFixed(4))} )`;switch(bt.getTransfer(n)){case lo:return[e,"LinearTransferOETF"];case Nt:return[e,"sRGBTransferOETF"];default:return ut("WebGLProgram: Unsupported color space: ",n),[e,"LinearTransferOETF"]}}function If(n,e,t){const i=n.getShaderParameter(e,n.COMPILE_STATUS),a=(n.getShaderInfoLog(e)||"").trim();if(i&&a==="")return"";const o=/ERROR: 0:(\d+)/.exec(a);if(o){const l=parseInt(o[1]);return t.toUpperCase()+`

`+a+`

`+dA(n.getShaderSource(e),l)}else return a}function hA(n,e){const t=fA(e);return[`vec4 ${n}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}const pA={[hp]:"Linear",[pp]:"Reinhard",[mp]:"Cineon",[hu]:"ACESFilmic",[_p]:"AgX",[vp]:"Neutral",[gp]:"Custom"};function mA(n,e){const t=pA[e];return t===void 0?(ut("WebGLProgram: Unsupported toneMapping:",e),"vec3 "+n+"( vec3 color ) { return LinearToneMapping( color ); }"):"vec3 "+n+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Hs=new ge;function gA(){bt.getLuminanceCoefficients(Hs);const n=Hs.x.toFixed(4),e=Hs.y.toFixed(4),t=Hs.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${n}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function _A(n){return[n.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",n.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Fa).join(`
`)}function vA(n){const e=[];for(const t in n){const i=n[t];i!==!1&&e.push("#define "+t+" "+i)}return e.join(`
`)}function xA(n,e){const t={},i=n.getProgramParameter(e,n.ACTIVE_ATTRIBUTES);for(let r=0;r<i;r++){const a=n.getActiveAttrib(e,r),o=a.name;let l=1;a.type===n.FLOAT_MAT2&&(l=2),a.type===n.FLOAT_MAT3&&(l=3),a.type===n.FLOAT_MAT4&&(l=4),t[o]={type:a.type,location:n.getAttribLocation(e,o),locationSize:l}}return t}function Fa(n){return n!==""}function Nf(n,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return n.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Pf(n,e){return n.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const bA=/^[ \t]*#include +<([\w\d./]+)>/gm;function Sc(n){return n.replace(bA,yA)}const SA=new Map;function yA(n,e){let t=_t[e];if(t===void 0){const i=SA.get(e);if(i!==void 0)t=_t[i],ut('WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,i);else throw new Error("THREE.WebGLProgram: Can not resolve #include <"+e+">")}return Sc(t)}const EA=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Lf(n){return n.replace(EA,MA)}function MA(n,e,t,i){let r="";for(let a=parseInt(e);a<parseInt(t);a++)r+=i.replace(/\[\s*i\s*\]/g,"[ "+a+" ]").replace(/UNROLLED_LOOP_INDEX/g,a);return r}function Df(n){let e=`precision ${n.precision} float;
	precision ${n.precision} int;
	precision ${n.precision} sampler2D;
	precision ${n.precision} samplerCube;
	precision ${n.precision} sampler3D;
	precision ${n.precision} sampler2DArray;
	precision ${n.precision} sampler2DShadow;
	precision ${n.precision} samplerCubeShadow;
	precision ${n.precision} sampler2DArrayShadow;
	precision ${n.precision} isampler2D;
	precision ${n.precision} isampler3D;
	precision ${n.precision} isamplerCube;
	precision ${n.precision} isampler2DArray;
	precision ${n.precision} usampler2D;
	precision ${n.precision} usampler3D;
	precision ${n.precision} usamplerCube;
	precision ${n.precision} usampler2DArray;
	`;return n.precision==="highp"?e+=`
#define HIGH_PRECISION`:n.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:n.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}const TA={[Vs]:"SHADOWMAP_TYPE_PCF",[Oa]:"SHADOWMAP_TYPE_VSM"};function wA(n){return TA[n.shadowMapType]||"SHADOWMAP_TYPE_BASIC"}const AA={[br]:"ENVMAP_TYPE_CUBE",[oa]:"ENVMAP_TYPE_CUBE",[bo]:"ENVMAP_TYPE_CUBE_UV"};function RA(n){return n.envMap===!1?"ENVMAP_TYPE_CUBE":AA[n.envMapMode]||"ENVMAP_TYPE_CUBE"}const CA={[oa]:"ENVMAP_MODE_REFRACTION"};function IA(n){return n.envMap===!1?"ENVMAP_MODE_REFLECTION":CA[n.envMapMode]||"ENVMAP_MODE_REFLECTION"}const NA={[fp]:"ENVMAP_BLENDING_MULTIPLY",[vE]:"ENVMAP_BLENDING_MIX",[xE]:"ENVMAP_BLENDING_ADD"};function PA(n){return n.envMap===!1?"ENVMAP_BLENDING_NONE":NA[n.combine]||"ENVMAP_BLENDING_NONE"}function LA(n){const e=n.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,i=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:i,maxMip:t}}function DA(n,e,t,i){const r=n.getContext(),a=t.defines;let o=t.vertexShader,l=t.fragmentShader;const c=wA(t),u=RA(t),f=IA(t),h=PA(t),d=LA(t),p=_A(t),m=vA(a),E=r.createProgram();let g,_,O=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(g=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(Fa).join(`
`),g.length>0&&(g+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(Fa).join(`
`),_.length>0&&(_+=`
`)):(g=[Df(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexNormals?"#define HAS_NORMAL":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Fa).join(`
`),_=[Df(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.envMap?"#define "+f:"",t.envMap?"#define "+h:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.packedNormalMap?"#define USE_PACKED_NORMALMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor?"#define USE_COLOR":"",t.vertexAlphas||t.batchingColor?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.numLightProbeGrids>0?"#define USE_LIGHT_PROBES_GRID":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==di?"#define TONE_MAPPING":"",t.toneMapping!==di?_t.tonemapping_pars_fragment:"",t.toneMapping!==di?mA("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",_t.colorspace_pars_fragment,hA("linearToOutputTexel",t.outputColorSpace),gA(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Fa).join(`
`)),o=Sc(o),o=Nf(o,t),o=Pf(o,t),l=Sc(l),l=Nf(l,t),l=Pf(l,t),o=Lf(o),l=Lf(l),t.isRawShaderMaterial!==!0&&(O=`#version 300 es
`,g=[p,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+g,_=["#define varying in",t.glslVersion===Wd?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Wd?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const D=O+g+o,y=O+_+l,B=Rf(r,r.VERTEX_SHADER,D),R=Rf(r,r.FRAGMENT_SHADER,y);r.attachShader(E,B),r.attachShader(E,R),t.index0AttributeName!==void 0?r.bindAttribLocation(E,0,t.index0AttributeName):t.hasPositionAttribute===!0&&r.bindAttribLocation(E,0,"position"),r.linkProgram(E);function C(z){if(n.debug.checkShaderErrors){const H=r.getProgramInfoLog(E)||"",q=r.getShaderInfoLog(B)||"",Q=r.getShaderInfoLog(R)||"",G=H.trim(),T=q.trim(),w=Q.trim();let I=!0,F=!0;if(r.getProgramParameter(E,r.LINK_STATUS)===!1)if(I=!1,typeof n.debug.onShaderError=="function")n.debug.onShaderError(r,E,B,R);else{const Y=If(r,B,"vertex"),te=If(r,R,"fragment");Rt("WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(E,r.VALIDATE_STATUS)+`

Material Name: `+z.name+`
Material Type: `+z.type+`

Program Info Log: `+G+`
`+Y+`
`+te)}else G!==""?ut("WebGLProgram: Program Info Log:",G):(T===""||w==="")&&(F=!1);F&&(z.diagnostics={runnable:I,programLog:G,vertexShader:{log:T,prefix:g},fragmentShader:{log:w,prefix:_}})}r.deleteShader(B),r.deleteShader(R),b=new Ys(r,E),A=xA(r,E)}let b;this.getUniforms=function(){return b===void 0&&C(this),b};let A;this.getAttributes=function(){return A===void 0&&C(this),A};let k=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return k===!1&&(k=r.getProgramParameter(E,cA)),k},this.destroy=function(){i.releaseStatesOfProgram(this),r.deleteProgram(E),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=uA++,this.cacheKey=e,this.usedTimes=1,this.program=E,this.vertexShader=B,this.fragmentShader=R,this}let kA=0;class UA{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e,t,i){const r=this._getShaderCacheForMaterial(e);return r.has(t)===!1&&(r.add(t),t.usedTimes++),r.has(i)===!1&&(r.add(i),i.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const i of t)i.usedTimes--,i.usedTimes===0&&this.shaderCache.delete(i.code);return this.materialCache.delete(e),this}getVertexShaderStage(e){return this._getShaderStage(e.vertexShader)}getFragmentShaderStage(e){return this._getShaderStage(e.fragmentShader)}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let i=t.get(e);return i===void 0&&(i=new Set,t.set(e,i)),i}_getShaderStage(e){const t=this.shaderCache;let i=t.get(e);return i===void 0&&(i=new OA(e),t.set(e,i)),i}}class OA{constructor(e){this.id=kA++,this.code=e,this.usedTimes=0}}function FA(n){return n===Sr||n===ao||n===so}function BA(n,e,t,i,r,a){const o=new Cp,l=new UA,c=new Set,u=[],f=new Map,h=i.logarithmicDepthBuffer;let d=i.precision;const p={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distance",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function m(b){return c.add(b),b===0?"uv":`uv${b}`}function E(b,A,k,z,H,q){const Q=z.fog,G=H.geometry,T=b.isMeshStandardMaterial||b.isMeshLambertMaterial||b.isMeshPhongMaterial?z.environment:null,w=b.isMeshStandardMaterial||b.isMeshLambertMaterial&&!b.envMap||b.isMeshPhongMaterial&&!b.envMap,I=e.get(b.envMap||T,w),F=I&&I.mapping===bo?I.image.height:null,Y=p[b.type];b.precision!==null&&(d=i.getMaxPrecision(b.precision),d!==b.precision&&ut("WebGLProgram.getParameters:",b.precision,"not supported, using",d,"instead."));const te=G.morphAttributes.position||G.morphAttributes.normal||G.morphAttributes.color,X=te!==void 0?te.length:0;let K=0;G.morphAttributes.position!==void 0&&(K=1),G.morphAttributes.normal!==void 0&&(K=2),G.morphAttributes.color!==void 0&&(K=3);let se,ne,N,V;if(Y){const $e=ri[Y];se=$e.vertexShader,ne=$e.fragmentShader}else{se=b.vertexShader,ne=b.fragmentShader;const $e=l.getVertexShaderStage(b),It=l.getFragmentShaderStage(b);l.update(b,$e,It),N=$e.id,V=It.id}const re=n.getRenderTarget(),Me=n.state.buffers.depth.getReversed(),fe=H.isInstancedMesh===!0,oe=H.isBatchedMesh===!0,ve=!!b.map,ye=!!b.matcap,Ie=!!I,be=!!b.aoMap,ke=!!b.lightMap,xe=!!b.bumpMap&&b.wireframe===!1,Ee=!!b.normalMap,_e=!!b.displacementMap,De=!!b.emissiveMap,Ne=!!b.metalnessMap,Oe=!!b.roughnessMap,J=b.anisotropy>0,We=b.clearcoat>0,Fe=b.dispersion>0,P=b.iridescence>0,x=b.sheen>0,Z=b.transmission>0,ae=J&&!!b.anisotropyMap,de=We&&!!b.clearcoatMap,Le=We&&!!b.clearcoatNormalMap,He=We&&!!b.clearcoatRoughnessMap,Se=P&&!!b.iridescenceMap,we=P&&!!b.iridescenceThicknessMap,Ge=x&&!!b.sheenColorMap,Je=x&&!!b.sheenRoughnessMap,Pe=!!b.specularMap,Ce=!!b.specularColorMap,qe=!!b.specularIntensityMap,je=Z&&!!b.transmissionMap,st=Z&&!!b.thicknessMap,ce=!!b.gradientMap,Be=!!b.alphaMap,Te=b.alphaTest>0,Ve=!!b.alphaHash,Ye=!!b.extensions;let Ue=di;b.toneMapped&&(re===null||re.isXRRenderTarget===!0)&&(Ue=n.toneMapping);const nt={shaderID:Y,shaderType:b.type,shaderName:b.name,vertexShader:se,fragmentShader:ne,defines:b.defines,customVertexShaderID:N,customFragmentShaderID:V,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:d,batching:oe,batchingColor:oe&&H._colorsTexture!==null,instancing:fe,instancingColor:fe&&H.instanceColor!==null,instancingMorph:fe&&H.morphTexture!==null,outputColorSpace:re===null?n.outputColorSpace:re.isXRRenderTarget===!0?re.texture.colorSpace:bt.workingColorSpace,alphaToCoverage:!!b.alphaToCoverage,map:ve,matcap:ye,envMap:Ie,envMapMode:Ie&&I.mapping,envMapCubeUVHeight:F,aoMap:be,lightMap:ke,bumpMap:xe,normalMap:Ee,displacementMap:_e,emissiveMap:De,normalMapObjectSpace:Ee&&b.normalMapType===yE,normalMapTangentSpace:Ee&&b.normalMapType===Hd,packedNormalMap:Ee&&b.normalMapType===Hd&&FA(b.normalMap.format),metalnessMap:Ne,roughnessMap:Oe,anisotropy:J,anisotropyMap:ae,clearcoat:We,clearcoatMap:de,clearcoatNormalMap:Le,clearcoatRoughnessMap:He,dispersion:Fe,iridescence:P,iridescenceMap:Se,iridescenceThicknessMap:we,sheen:x,sheenColorMap:Ge,sheenRoughnessMap:Je,specularMap:Pe,specularColorMap:Ce,specularIntensityMap:qe,transmission:Z,transmissionMap:je,thicknessMap:st,gradientMap:ce,opaque:b.transparent===!1&&b.blending===na&&b.alphaToCoverage===!1,alphaMap:Be,alphaTest:Te,alphaHash:Ve,combine:b.combine,mapUv:ve&&m(b.map.channel),aoMapUv:be&&m(b.aoMap.channel),lightMapUv:ke&&m(b.lightMap.channel),bumpMapUv:xe&&m(b.bumpMap.channel),normalMapUv:Ee&&m(b.normalMap.channel),displacementMapUv:_e&&m(b.displacementMap.channel),emissiveMapUv:De&&m(b.emissiveMap.channel),metalnessMapUv:Ne&&m(b.metalnessMap.channel),roughnessMapUv:Oe&&m(b.roughnessMap.channel),anisotropyMapUv:ae&&m(b.anisotropyMap.channel),clearcoatMapUv:de&&m(b.clearcoatMap.channel),clearcoatNormalMapUv:Le&&m(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:He&&m(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Se&&m(b.iridescenceMap.channel),iridescenceThicknessMapUv:we&&m(b.iridescenceThicknessMap.channel),sheenColorMapUv:Ge&&m(b.sheenColorMap.channel),sheenRoughnessMapUv:Je&&m(b.sheenRoughnessMap.channel),specularMapUv:Pe&&m(b.specularMap.channel),specularColorMapUv:Ce&&m(b.specularColorMap.channel),specularIntensityMapUv:qe&&m(b.specularIntensityMap.channel),transmissionMapUv:je&&m(b.transmissionMap.channel),thicknessMapUv:st&&m(b.thicknessMap.channel),alphaMapUv:Be&&m(b.alphaMap.channel),vertexTangents:!!G.attributes.tangent&&(Ee||J),vertexNormals:!!G.attributes.normal,vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!G.attributes.color&&G.attributes.color.itemSize===4,pointsUvs:H.isPoints===!0&&!!G.attributes.uv&&(ve||Be),fog:!!Q,useFog:b.fog===!0,fogExp2:!!Q&&Q.isFogExp2,flatShading:b.wireframe===!1&&(b.flatShading===!0||G.attributes.normal===void 0&&Ee===!1&&(b.isMeshLambertMaterial||b.isMeshPhongMaterial||b.isMeshStandardMaterial||b.isMeshPhysicalMaterial)),sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:h,reversedDepthBuffer:Me,skinning:H.isSkinnedMesh===!0,hasPositionAttribute:G.attributes.position!==void 0,morphTargets:G.morphAttributes.position!==void 0,morphNormals:G.morphAttributes.normal!==void 0,morphColors:G.morphAttributes.color!==void 0,morphTargetsCount:X,morphTextureStride:K,numDirLights:A.directional.length,numPointLights:A.point.length,numSpotLights:A.spot.length,numSpotLightMaps:A.spotLightMap.length,numRectAreaLights:A.rectArea.length,numHemiLights:A.hemi.length,numDirLightShadows:A.directionalShadowMap.length,numPointLightShadows:A.pointShadowMap.length,numSpotLightShadows:A.spotShadowMap.length,numSpotLightShadowsWithMaps:A.numSpotLightShadowsWithMaps,numLightProbes:A.numLightProbes,numLightProbeGrids:q.length,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:b.dithering,shadowMapEnabled:n.shadowMap.enabled&&k.length>0,shadowMapType:n.shadowMap.type,toneMapping:Ue,decodeVideoTexture:ve&&b.map.isVideoTexture===!0&&bt.getTransfer(b.map.colorSpace)===Nt,decodeVideoTextureEmissive:De&&b.emissiveMap.isVideoTexture===!0&&bt.getTransfer(b.emissiveMap.colorSpace)===Nt,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===oi,flipSided:b.side===yn,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:Ye&&b.extensions.clipCullDistance===!0&&t.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Ye&&b.extensions.multiDraw===!0||oe)&&t.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:t.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return nt.vertexUv1s=c.has(1),nt.vertexUv2s=c.has(2),nt.vertexUv3s=c.has(3),c.clear(),nt}function g(b){const A=[];if(b.shaderID?A.push(b.shaderID):(A.push(b.customVertexShaderID),A.push(b.customFragmentShaderID)),b.defines!==void 0)for(const k in b.defines)A.push(k),A.push(b.defines[k]);return b.isRawShaderMaterial===!1&&(_(A,b),O(A,b),A.push(n.outputColorSpace)),A.push(b.customProgramCacheKey),A.join()}function _(b,A){b.push(A.precision),b.push(A.outputColorSpace),b.push(A.envMapMode),b.push(A.envMapCubeUVHeight),b.push(A.mapUv),b.push(A.alphaMapUv),b.push(A.lightMapUv),b.push(A.aoMapUv),b.push(A.bumpMapUv),b.push(A.normalMapUv),b.push(A.displacementMapUv),b.push(A.emissiveMapUv),b.push(A.metalnessMapUv),b.push(A.roughnessMapUv),b.push(A.anisotropyMapUv),b.push(A.clearcoatMapUv),b.push(A.clearcoatNormalMapUv),b.push(A.clearcoatRoughnessMapUv),b.push(A.iridescenceMapUv),b.push(A.iridescenceThicknessMapUv),b.push(A.sheenColorMapUv),b.push(A.sheenRoughnessMapUv),b.push(A.specularMapUv),b.push(A.specularColorMapUv),b.push(A.specularIntensityMapUv),b.push(A.transmissionMapUv),b.push(A.thicknessMapUv),b.push(A.combine),b.push(A.fogExp2),b.push(A.sizeAttenuation),b.push(A.morphTargetsCount),b.push(A.morphAttributeCount),b.push(A.numDirLights),b.push(A.numPointLights),b.push(A.numSpotLights),b.push(A.numSpotLightMaps),b.push(A.numHemiLights),b.push(A.numRectAreaLights),b.push(A.numDirLightShadows),b.push(A.numPointLightShadows),b.push(A.numSpotLightShadows),b.push(A.numSpotLightShadowsWithMaps),b.push(A.numLightProbes),b.push(A.shadowMapType),b.push(A.toneMapping),b.push(A.numClippingPlanes),b.push(A.numClipIntersection),b.push(A.depthPacking)}function O(b,A){o.disableAll(),A.instancing&&o.enable(0),A.instancingColor&&o.enable(1),A.instancingMorph&&o.enable(2),A.matcap&&o.enable(3),A.envMap&&o.enable(4),A.normalMapObjectSpace&&o.enable(5),A.normalMapTangentSpace&&o.enable(6),A.clearcoat&&o.enable(7),A.iridescence&&o.enable(8),A.alphaTest&&o.enable(9),A.vertexColors&&o.enable(10),A.vertexAlphas&&o.enable(11),A.vertexUv1s&&o.enable(12),A.vertexUv2s&&o.enable(13),A.vertexUv3s&&o.enable(14),A.vertexTangents&&o.enable(15),A.anisotropy&&o.enable(16),A.alphaHash&&o.enable(17),A.batching&&o.enable(18),A.dispersion&&o.enable(19),A.batchingColor&&o.enable(20),A.gradientMap&&o.enable(21),A.packedNormalMap&&o.enable(22),A.vertexNormals&&o.enable(23),b.push(o.mask),o.disableAll(),A.fog&&o.enable(0),A.useFog&&o.enable(1),A.flatShading&&o.enable(2),A.logarithmicDepthBuffer&&o.enable(3),A.reversedDepthBuffer&&o.enable(4),A.skinning&&o.enable(5),A.morphTargets&&o.enable(6),A.morphNormals&&o.enable(7),A.morphColors&&o.enable(8),A.premultipliedAlpha&&o.enable(9),A.shadowMapEnabled&&o.enable(10),A.doubleSided&&o.enable(11),A.flipSided&&o.enable(12),A.useDepthPacking&&o.enable(13),A.dithering&&o.enable(14),A.transmission&&o.enable(15),A.sheen&&o.enable(16),A.opaque&&o.enable(17),A.pointsUvs&&o.enable(18),A.decodeVideoTexture&&o.enable(19),A.decodeVideoTextureEmissive&&o.enable(20),A.alphaToCoverage&&o.enable(21),A.numLightProbeGrids>0&&o.enable(22),A.hasPositionAttribute&&o.enable(23),b.push(o.mask)}function D(b){const A=p[b.type];let k;if(A){const z=ri[A];k=sM.clone(z.uniforms)}else k=b.uniforms;return k}function y(b,A){let k=f.get(A);return k!==void 0?++k.usedTimes:(k=new DA(n,A,b,r),u.push(k),f.set(A,k)),k}function B(b){if(--b.usedTimes===0){const A=u.indexOf(b);u[A]=u[u.length-1],u.pop(),f.delete(b.cacheKey),b.destroy()}}function R(b){l.remove(b)}function C(){l.dispose()}return{getParameters:E,getProgramCacheKey:g,getUniforms:D,acquireProgram:y,releaseProgram:B,releaseShaderCache:R,programs:u,dispose:C}}function zA(){let n=new WeakMap;function e(o){return n.has(o)}function t(o){let l=n.get(o);return l===void 0&&(l={},n.set(o,l)),l}function i(o){n.delete(o)}function r(o,l,c){n.get(o)[l]=c}function a(){n=new WeakMap}return{has:e,get:t,remove:i,update:r,dispose:a}}function HA(n,e){return n.groupOrder!==e.groupOrder?n.groupOrder-e.groupOrder:n.renderOrder!==e.renderOrder?n.renderOrder-e.renderOrder:n.material.id!==e.material.id?n.material.id-e.material.id:n.materialVariant!==e.materialVariant?n.materialVariant-e.materialVariant:n.z!==e.z?n.z-e.z:n.id-e.id}function kf(n,e){return n.groupOrder!==e.groupOrder?n.groupOrder-e.groupOrder:n.renderOrder!==e.renderOrder?n.renderOrder-e.renderOrder:n.z!==e.z?e.z-n.z:n.id-e.id}function Uf(){const n=[];let e=0;const t=[],i=[],r=[];function a(){e=0,t.length=0,i.length=0,r.length=0}function o(d){let p=0;return d.isInstancedMesh&&(p+=2),d.isSkinnedMesh&&(p+=1),p}function l(d,p,m,E,g,_){let O=n[e];return O===void 0?(O={id:d.id,object:d,geometry:p,material:m,materialVariant:o(d),groupOrder:E,renderOrder:d.renderOrder,z:g,group:_},n[e]=O):(O.id=d.id,O.object=d,O.geometry=p,O.material=m,O.materialVariant=o(d),O.groupOrder=E,O.renderOrder=d.renderOrder,O.z=g,O.group=_),e++,O}function c(d,p,m,E,g,_){const O=l(d,p,m,E,g,_);m.transmission>0?i.push(O):m.transparent===!0?r.push(O):t.push(O)}function u(d,p,m,E,g,_){const O=l(d,p,m,E,g,_);m.transmission>0?i.unshift(O):m.transparent===!0?r.unshift(O):t.unshift(O)}function f(d,p,m){t.length>1&&t.sort(d||HA),i.length>1&&i.sort(p||kf),r.length>1&&r.sort(p||kf),m&&(t.reverse(),i.reverse(),r.reverse())}function h(){for(let d=e,p=n.length;d<p;d++){const m=n[d];if(m.id===null)break;m.id=null,m.object=null,m.geometry=null,m.material=null,m.group=null}}return{opaque:t,transmissive:i,transparent:r,init:a,push:c,unshift:u,finish:h,sort:f}}function GA(){let n=new WeakMap;function e(i,r){const a=n.get(i);let o;return a===void 0?(o=new Uf,n.set(i,[o])):r>=a.length?(o=new Uf,a.push(o)):o=a[r],o}function t(){n=new WeakMap}return{get:e,dispose:t}}function VA(){const n={};return{get:function(e){if(n[e.id]!==void 0)return n[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new ge,color:new Ct};break;case"SpotLight":t={position:new ge,direction:new ge,color:new Ct,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new ge,color:new Ct,distance:0,decay:0};break;case"HemisphereLight":t={direction:new ge,skyColor:new Ct,groundColor:new Ct};break;case"RectAreaLight":t={color:new Ct,position:new ge,halfWidth:new ge,halfHeight:new ge};break}return n[e.id]=t,t}}}function WA(){const n={};return{get:function(e){if(n[e.id]!==void 0)return n[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new xt};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new xt};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new xt,shadowCameraNear:1,shadowCameraFar:1e3};break}return n[e.id]=t,t}}}let $A=0;function XA(n,e){return(e.castShadow?2:0)-(n.castShadow?2:0)+(e.map?1:0)-(n.map?1:0)}function qA(n){const e=new VA,t=WA(),i={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let u=0;u<9;u++)i.probe.push(new ge);const r=new ge,a=new Xt,o=new Xt;function l(u){let f=0,h=0,d=0;for(let A=0;A<9;A++)i.probe[A].set(0,0,0);let p=0,m=0,E=0,g=0,_=0,O=0,D=0,y=0,B=0,R=0,C=0;u.sort(XA);for(let A=0,k=u.length;A<k;A++){const z=u[A],H=z.color,q=z.intensity,Q=z.distance;let G=null;if(z.shadow&&z.shadow.map&&(z.shadow.map.texture.format===Sr?G=z.shadow.map.texture:G=z.shadow.map.depthTexture||z.shadow.map.texture),z.isAmbientLight)f+=H.r*q,h+=H.g*q,d+=H.b*q;else if(z.isLightProbe){for(let T=0;T<9;T++)i.probe[T].addScaledVector(z.sh.coefficients[T],q);C++}else if(z.isDirectionalLight){const T=e.get(z);if(T.color.copy(z.color).multiplyScalar(z.intensity),z.castShadow){const w=z.shadow,I=t.get(z);I.shadowIntensity=w.intensity,I.shadowBias=w.bias,I.shadowNormalBias=w.normalBias,I.shadowRadius=w.radius,I.shadowMapSize=w.mapSize,i.directionalShadow[p]=I,i.directionalShadowMap[p]=G,i.directionalShadowMatrix[p]=z.shadow.matrix,O++}i.directional[p]=T,p++}else if(z.isSpotLight){const T=e.get(z);T.position.setFromMatrixPosition(z.matrixWorld),T.color.copy(H).multiplyScalar(q),T.distance=Q,T.coneCos=Math.cos(z.angle),T.penumbraCos=Math.cos(z.angle*(1-z.penumbra)),T.decay=z.decay,i.spot[E]=T;const w=z.shadow;if(z.map&&(i.spotLightMap[B]=z.map,B++,w.updateMatrices(z),z.castShadow&&R++),i.spotLightMatrix[E]=w.matrix,z.castShadow){const I=t.get(z);I.shadowIntensity=w.intensity,I.shadowBias=w.bias,I.shadowNormalBias=w.normalBias,I.shadowRadius=w.radius,I.shadowMapSize=w.mapSize,i.spotShadow[E]=I,i.spotShadowMap[E]=G,y++}E++}else if(z.isRectAreaLight){const T=e.get(z);T.color.copy(H).multiplyScalar(q),T.halfWidth.set(z.width*.5,0,0),T.halfHeight.set(0,z.height*.5,0),i.rectArea[g]=T,g++}else if(z.isPointLight){const T=e.get(z);if(T.color.copy(z.color).multiplyScalar(z.intensity),T.distance=z.distance,T.decay=z.decay,z.castShadow){const w=z.shadow,I=t.get(z);I.shadowIntensity=w.intensity,I.shadowBias=w.bias,I.shadowNormalBias=w.normalBias,I.shadowRadius=w.radius,I.shadowMapSize=w.mapSize,I.shadowCameraNear=w.camera.near,I.shadowCameraFar=w.camera.far,i.pointShadow[m]=I,i.pointShadowMap[m]=G,i.pointShadowMatrix[m]=z.shadow.matrix,D++}i.point[m]=T,m++}else if(z.isHemisphereLight){const T=e.get(z);T.skyColor.copy(z.color).multiplyScalar(q),T.groundColor.copy(z.groundColor).multiplyScalar(q),i.hemi[_]=T,_++}}g>0&&(n.has("OES_texture_float_linear")===!0?(i.rectAreaLTC1=Ze.LTC_FLOAT_1,i.rectAreaLTC2=Ze.LTC_FLOAT_2):(i.rectAreaLTC1=Ze.LTC_HALF_1,i.rectAreaLTC2=Ze.LTC_HALF_2)),i.ambient[0]=f,i.ambient[1]=h,i.ambient[2]=d;const b=i.hash;(b.directionalLength!==p||b.pointLength!==m||b.spotLength!==E||b.rectAreaLength!==g||b.hemiLength!==_||b.numDirectionalShadows!==O||b.numPointShadows!==D||b.numSpotShadows!==y||b.numSpotMaps!==B||b.numLightProbes!==C)&&(i.directional.length=p,i.spot.length=E,i.rectArea.length=g,i.point.length=m,i.hemi.length=_,i.directionalShadow.length=O,i.directionalShadowMap.length=O,i.pointShadow.length=D,i.pointShadowMap.length=D,i.spotShadow.length=y,i.spotShadowMap.length=y,i.directionalShadowMatrix.length=O,i.pointShadowMatrix.length=D,i.spotLightMatrix.length=y+B-R,i.spotLightMap.length=B,i.numSpotLightShadowsWithMaps=R,i.numLightProbes=C,b.directionalLength=p,b.pointLength=m,b.spotLength=E,b.rectAreaLength=g,b.hemiLength=_,b.numDirectionalShadows=O,b.numPointShadows=D,b.numSpotShadows=y,b.numSpotMaps=B,b.numLightProbes=C,i.version=$A++)}function c(u,f){let h=0,d=0,p=0,m=0,E=0;const g=f.matrixWorldInverse;for(let _=0,O=u.length;_<O;_++){const D=u[_];if(D.isDirectionalLight){const y=i.directional[h];y.direction.setFromMatrixPosition(D.matrixWorld),r.setFromMatrixPosition(D.target.matrixWorld),y.direction.sub(r),y.direction.transformDirection(g),h++}else if(D.isSpotLight){const y=i.spot[p];y.position.setFromMatrixPosition(D.matrixWorld),y.position.applyMatrix4(g),y.direction.setFromMatrixPosition(D.matrixWorld),r.setFromMatrixPosition(D.target.matrixWorld),y.direction.sub(r),y.direction.transformDirection(g),p++}else if(D.isRectAreaLight){const y=i.rectArea[m];y.position.setFromMatrixPosition(D.matrixWorld),y.position.applyMatrix4(g),o.identity(),a.copy(D.matrixWorld),a.premultiply(g),o.extractRotation(a),y.halfWidth.set(D.width*.5,0,0),y.halfHeight.set(0,D.height*.5,0),y.halfWidth.applyMatrix4(o),y.halfHeight.applyMatrix4(o),m++}else if(D.isPointLight){const y=i.point[d];y.position.setFromMatrixPosition(D.matrixWorld),y.position.applyMatrix4(g),d++}else if(D.isHemisphereLight){const y=i.hemi[E];y.direction.setFromMatrixPosition(D.matrixWorld),y.direction.transformDirection(g),E++}}}return{setup:l,setupView:c,state:i}}function Of(n){const e=new qA(n),t=[],i=[],r=[];function a(d){h.camera=d,t.length=0,i.length=0,r.length=0}function o(d){t.push(d)}function l(d){i.push(d)}function c(d){r.push(d)}function u(){e.setup(t)}function f(d){e.setupView(t,d)}const h={lightsArray:t,shadowsArray:i,lightProbeGridArray:r,camera:null,lights:e,transmissionRenderTarget:{},textureUnits:0};return{init:a,state:h,setupLights:u,setupLightsView:f,pushLight:o,pushShadow:l,pushLightProbeGrid:c}}function YA(n){let e=new WeakMap;function t(r,a=0){const o=e.get(r);let l;return o===void 0?(l=new Of(n),e.set(r,[l])):a>=o.length?(l=new Of(n),o.push(l)):l=o[a],l}function i(){e=new WeakMap}return{get:t,dispose:i}}const KA=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,ZA=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,JA=[new ge(1,0,0),new ge(-1,0,0),new ge(0,1,0),new ge(0,-1,0),new ge(0,0,1),new ge(0,0,-1)],QA=[new ge(0,-1,0),new ge(0,-1,0),new ge(0,0,1),new ge(0,0,-1),new ge(0,-1,0),new ge(0,-1,0)],Ff=new Xt,Na=new ge,xl=new ge;function jA(n,e,t){let i=new Mu;const r=new xt,a=new xt,o=new Gt,l=new uM,c=new dM,u={},f=t.maxTextureSize,h={[ir]:yn,[yn]:ir,[oi]:oi},d=new Kn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new xt},radius:{value:4}},vertexShader:KA,fragmentShader:ZA}),p=d.clone();p.defines.HORIZONTAL_PASS=1;const m=new vi;m.setAttribute("position",new hi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const E=new gi(m,d),g=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Vs;let _=this.type;this.render=function(R,C,b){if(g.enabled===!1||g.autoUpdate===!1&&g.needsUpdate===!1||R.length===0)return;this.type===jy&&(ut("WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead."),this.type=Vs);const A=n.getRenderTarget(),k=n.getActiveCubeFace(),z=n.getActiveMipmapLevel(),H=n.state;H.setBlending(Ri),H.buffers.depth.getReversed()===!0?H.buffers.color.setClear(0,0,0,0):H.buffers.color.setClear(1,1,1,1),H.buffers.depth.setTest(!0),H.setScissorTest(!1);const q=_!==this.type;q&&C.traverse(function(Q){Q.material&&(Array.isArray(Q.material)?Q.material.forEach(G=>G.needsUpdate=!0):Q.material.needsUpdate=!0)});for(let Q=0,G=R.length;Q<G;Q++){const T=R[Q],w=T.shadow;if(w===void 0){ut("WebGLShadowMap:",T,"has no shadow.");continue}if(w.autoUpdate===!1&&w.needsUpdate===!1)continue;r.copy(w.mapSize);const I=w.getFrameExtents();r.multiply(I),a.copy(w.mapSize),(r.x>f||r.y>f)&&(r.x>f&&(a.x=Math.floor(f/I.x),r.x=a.x*I.x,w.mapSize.x=a.x),r.y>f&&(a.y=Math.floor(f/I.y),r.y=a.y*I.y,w.mapSize.y=a.y));const F=n.state.buffers.depth.getReversed();if(w.camera._reversedDepth=F,w.map===null||q===!0){if(w.map!==null&&(w.map.depthTexture!==null&&(w.map.depthTexture.dispose(),w.map.depthTexture=null),w.map.dispose()),this.type===Oa){if(T.isPointLight){ut("WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.");continue}w.map=new fi(r.x,r.y,{format:Sr,type:ki,minFilter:fn,magFilter:fn,generateMipmaps:!1}),w.map.texture.name=T.name+".shadowMap",w.map.depthTexture=new la(r.x,r.y,ci),w.map.depthTexture.name=T.name+".shadowMapDepth",w.map.depthTexture.format=Ui,w.map.depthTexture.compareFunction=null,w.map.depthTexture.minFilter=an,w.map.depthTexture.magFilter=an}else T.isPointLight?(w.map=new Gp(r.x),w.map.depthTexture=new rM(r.x,mi)):(w.map=new fi(r.x,r.y),w.map.depthTexture=new la(r.x,r.y,mi)),w.map.depthTexture.name=T.name+".shadowMap",w.map.depthTexture.format=Ui,this.type===Vs?(w.map.depthTexture.compareFunction=F?Su:bu,w.map.depthTexture.minFilter=fn,w.map.depthTexture.magFilter=fn):(w.map.depthTexture.compareFunction=null,w.map.depthTexture.minFilter=an,w.map.depthTexture.magFilter=an);w.camera.updateProjectionMatrix()}const Y=w.map.isWebGLCubeRenderTarget?6:1;for(let te=0;te<Y;te++){if(w.map.isWebGLCubeRenderTarget)n.setRenderTarget(w.map,te),n.clear();else{te===0&&(n.setRenderTarget(w.map),n.clear());const X=w.getViewport(te);o.set(a.x*X.x,a.y*X.y,a.x*X.z,a.y*X.w),H.viewport(o)}if(T.isPointLight){const X=w.camera,K=w.matrix,se=T.distance||X.far;se!==X.far&&(X.far=se,X.updateProjectionMatrix()),Na.setFromMatrixPosition(T.matrixWorld),X.position.copy(Na),xl.copy(X.position),xl.add(JA[te]),X.up.copy(QA[te]),X.lookAt(xl),X.updateMatrixWorld(),K.makeTranslation(-Na.x,-Na.y,-Na.z),Ff.multiplyMatrices(X.projectionMatrix,X.matrixWorldInverse),w._frustum.setFromProjectionMatrix(Ff,X.coordinateSystem,X.reversedDepth)}else w.updateMatrices(T);i=w.getFrustum(),y(C,b,w.camera,T,this.type)}w.isPointLightShadow!==!0&&this.type===Oa&&O(w,b),w.needsUpdate=!1}_=this.type,g.needsUpdate=!1,n.setRenderTarget(A,k,z)};function O(R,C){const b=e.update(E);d.defines.VSM_SAMPLES!==R.blurSamples&&(d.defines.VSM_SAMPLES=R.blurSamples,p.defines.VSM_SAMPLES=R.blurSamples,d.needsUpdate=!0,p.needsUpdate=!0),R.mapPass===null&&(R.mapPass=new fi(r.x,r.y,{format:Sr,type:ki})),d.uniforms.shadow_pass.value=R.map.depthTexture,d.uniforms.resolution.value=R.mapSize,d.uniforms.radius.value=R.radius,n.setRenderTarget(R.mapPass),n.clear(),n.renderBufferDirect(C,null,b,d,E,null),p.uniforms.shadow_pass.value=R.mapPass.texture,p.uniforms.resolution.value=R.mapSize,p.uniforms.radius.value=R.radius,n.setRenderTarget(R.map),n.clear(),n.renderBufferDirect(C,null,b,p,E,null)}function D(R,C,b,A){let k=null;const z=b.isPointLight===!0?R.customDistanceMaterial:R.customDepthMaterial;if(z!==void 0)k=z;else if(k=b.isPointLight===!0?c:l,n.localClippingEnabled&&C.clipShadows===!0&&Array.isArray(C.clippingPlanes)&&C.clippingPlanes.length!==0||C.displacementMap&&C.displacementScale!==0||C.alphaMap&&C.alphaTest>0||C.map&&C.alphaTest>0||C.alphaToCoverage===!0){const H=k.uuid,q=C.uuid;let Q=u[H];Q===void 0&&(Q={},u[H]=Q);let G=Q[q];G===void 0&&(G=k.clone(),Q[q]=G,C.addEventListener("dispose",B)),k=G}if(k.visible=C.visible,k.wireframe=C.wireframe,A===Oa?k.side=C.shadowSide!==null?C.shadowSide:C.side:k.side=C.shadowSide!==null?C.shadowSide:h[C.side],k.alphaMap=C.alphaMap,k.alphaTest=C.alphaToCoverage===!0?.5:C.alphaTest,k.map=C.map,k.clipShadows=C.clipShadows,k.clippingPlanes=C.clippingPlanes,k.clipIntersection=C.clipIntersection,k.displacementMap=C.displacementMap,k.displacementScale=C.displacementScale,k.displacementBias=C.displacementBias,k.wireframeLinewidth=C.wireframeLinewidth,k.linewidth=C.linewidth,b.isPointLight===!0&&k.isMeshDistanceMaterial===!0){const H=n.properties.get(k);H.light=b}return k}function y(R,C,b,A,k){if(R.visible===!1)return;if(R.layers.test(C.layers)&&(R.isMesh||R.isLine||R.isPoints)&&(R.castShadow||R.receiveShadow&&k===Oa)&&(!R.frustumCulled||i.intersectsObject(R))){R.modelViewMatrix.multiplyMatrices(b.matrixWorldInverse,R.matrixWorld);const q=e.update(R),Q=R.material;if(Array.isArray(Q)){const G=q.groups;for(let T=0,w=G.length;T<w;T++){const I=G[T],F=Q[I.materialIndex];if(F&&F.visible){const Y=D(R,F,A,k);R.onBeforeShadow(n,R,C,b,q,Y,I),n.renderBufferDirect(b,null,q,Y,R,I),R.onAfterShadow(n,R,C,b,q,Y,I)}}}else if(Q.visible){const G=D(R,Q,A,k);R.onBeforeShadow(n,R,C,b,q,G,null),n.renderBufferDirect(b,null,q,G,R,null),R.onAfterShadow(n,R,C,b,q,G,null)}}const H=R.children;for(let q=0,Q=H.length;q<Q;q++)y(H[q],C,b,A,k)}function B(R){R.target.removeEventListener("dispose",B);for(const b in u){const A=u[b],k=R.target.uuid;k in A&&(A[k].dispose(),delete A[k])}}}function eR(n,e){function t(){let ce=!1;const Be=new Gt;let Te=null;const Ve=new Gt(0,0,0,0);return{setMask:function(Ye){Te!==Ye&&!ce&&(n.colorMask(Ye,Ye,Ye,Ye),Te=Ye)},setLocked:function(Ye){ce=Ye},setClear:function(Ye,Ue,nt,$e,It){It===!0&&(Ye*=$e,Ue*=$e,nt*=$e),Be.set(Ye,Ue,nt,$e),Ve.equals(Be)===!1&&(n.clearColor(Ye,Ue,nt,$e),Ve.copy(Be))},reset:function(){ce=!1,Te=null,Ve.set(-1,0,0,0)}}}function i(){let ce=!1,Be=!1,Te=null,Ve=null,Ye=null;return{setReversed:function(Ue){if(Be!==Ue){const nt=e.get("EXT_clip_control");Ue?nt.clipControlEXT(nt.LOWER_LEFT_EXT,nt.ZERO_TO_ONE_EXT):nt.clipControlEXT(nt.LOWER_LEFT_EXT,nt.NEGATIVE_ONE_TO_ONE_EXT),Be=Ue;const $e=Ye;Ye=null,this.setClear($e)}},getReversed:function(){return Be},setTest:function(Ue){Ue?re(n.DEPTH_TEST):Me(n.DEPTH_TEST)},setMask:function(Ue){Te!==Ue&&!ce&&(n.depthMask(Ue),Te=Ue)},setFunc:function(Ue){if(Be&&(Ue=PE[Ue]),Ve!==Ue){switch(Ue){case Dl:n.depthFunc(n.NEVER);break;case kl:n.depthFunc(n.ALWAYS);break;case Ul:n.depthFunc(n.LESS);break;case sa:n.depthFunc(n.LEQUAL);break;case Ol:n.depthFunc(n.EQUAL);break;case Fl:n.depthFunc(n.GEQUAL);break;case Bl:n.depthFunc(n.GREATER);break;case zl:n.depthFunc(n.NOTEQUAL);break;default:n.depthFunc(n.LEQUAL)}Ve=Ue}},setLocked:function(Ue){ce=Ue},setClear:function(Ue){Ye!==Ue&&(Ye=Ue,Be&&(Ue=1-Ue),n.clearDepth(Ue))},reset:function(){ce=!1,Te=null,Ve=null,Ye=null,Be=!1}}}function r(){let ce=!1,Be=null,Te=null,Ve=null,Ye=null,Ue=null,nt=null,$e=null,It=null;return{setTest:function(yt){ce||(yt?re(n.STENCIL_TEST):Me(n.STENCIL_TEST))},setMask:function(yt){Be!==yt&&!ce&&(n.stencilMask(yt),Be=yt)},setFunc:function(yt,Mn,xn){(Te!==yt||Ve!==Mn||Ye!==xn)&&(n.stencilFunc(yt,Mn,xn),Te=yt,Ve=Mn,Ye=xn)},setOp:function(yt,Mn,xn){(Ue!==yt||nt!==Mn||$e!==xn)&&(n.stencilOp(yt,Mn,xn),Ue=yt,nt=Mn,$e=xn)},setLocked:function(yt){ce=yt},setClear:function(yt){It!==yt&&(n.clearStencil(yt),It=yt)},reset:function(){ce=!1,Be=null,Te=null,Ve=null,Ye=null,Ue=null,nt=null,$e=null,It=null}}}const a=new t,o=new i,l=new r,c=new WeakMap,u=new WeakMap;let f={},h={},d={},p=new WeakMap,m=[],E=null,g=!1,_=null,O=null,D=null,y=null,B=null,R=null,C=null,b=new Ct(0,0,0),A=0,k=!1,z=null,H=null,q=null,Q=null,G=null;const T=n.getParameter(n.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let w=!1,I=0;const F=n.getParameter(n.VERSION);F.indexOf("WebGL")!==-1?(I=parseFloat(/^WebGL (\d)/.exec(F)[1]),w=I>=1):F.indexOf("OpenGL ES")!==-1&&(I=parseFloat(/^OpenGL ES (\d)/.exec(F)[1]),w=I>=2);let Y=null,te={};const X=n.getParameter(n.SCISSOR_BOX),K=n.getParameter(n.VIEWPORT),se=new Gt().fromArray(X),ne=new Gt().fromArray(K);function N(ce,Be,Te,Ve){const Ye=new Uint8Array(4),Ue=n.createTexture();n.bindTexture(ce,Ue),n.texParameteri(ce,n.TEXTURE_MIN_FILTER,n.NEAREST),n.texParameteri(ce,n.TEXTURE_MAG_FILTER,n.NEAREST);for(let nt=0;nt<Te;nt++)ce===n.TEXTURE_3D||ce===n.TEXTURE_2D_ARRAY?n.texImage3D(Be,0,n.RGBA,1,1,Ve,0,n.RGBA,n.UNSIGNED_BYTE,Ye):n.texImage2D(Be+nt,0,n.RGBA,1,1,0,n.RGBA,n.UNSIGNED_BYTE,Ye);return Ue}const V={};V[n.TEXTURE_2D]=N(n.TEXTURE_2D,n.TEXTURE_2D,1),V[n.TEXTURE_CUBE_MAP]=N(n.TEXTURE_CUBE_MAP,n.TEXTURE_CUBE_MAP_POSITIVE_X,6),V[n.TEXTURE_2D_ARRAY]=N(n.TEXTURE_2D_ARRAY,n.TEXTURE_2D_ARRAY,1,1),V[n.TEXTURE_3D]=N(n.TEXTURE_3D,n.TEXTURE_3D,1,1),a.setClear(0,0,0,1),o.setClear(1),l.setClear(0),re(n.DEPTH_TEST),o.setFunc(sa),xe(!1),Ee(Od),re(n.CULL_FACE),be(Ri);function re(ce){f[ce]!==!0&&(n.enable(ce),f[ce]=!0)}function Me(ce){f[ce]!==!1&&(n.disable(ce),f[ce]=!1)}function fe(ce,Be){return d[ce]!==Be?(n.bindFramebuffer(ce,Be),d[ce]=Be,ce===n.DRAW_FRAMEBUFFER&&(d[n.FRAMEBUFFER]=Be),ce===n.FRAMEBUFFER&&(d[n.DRAW_FRAMEBUFFER]=Be),!0):!1}function oe(ce,Be){let Te=m,Ve=!1;if(ce){Te=p.get(Be),Te===void 0&&(Te=[],p.set(Be,Te));const Ye=ce.textures;if(Te.length!==Ye.length||Te[0]!==n.COLOR_ATTACHMENT0){for(let Ue=0,nt=Ye.length;Ue<nt;Ue++)Te[Ue]=n.COLOR_ATTACHMENT0+Ue;Te.length=Ye.length,Ve=!0}}else Te[0]!==n.BACK&&(Te[0]=n.BACK,Ve=!0);Ve&&n.drawBuffers(Te)}function ve(ce){return E!==ce?(n.useProgram(ce),E=ce,!0):!1}const ye={[fr]:n.FUNC_ADD,[tE]:n.FUNC_SUBTRACT,[nE]:n.FUNC_REVERSE_SUBTRACT};ye[iE]=n.MIN,ye[rE]=n.MAX;const Ie={[aE]:n.ZERO,[sE]:n.ONE,[oE]:n.SRC_COLOR,[Pl]:n.SRC_ALPHA,[hE]:n.SRC_ALPHA_SATURATE,[dE]:n.DST_COLOR,[cE]:n.DST_ALPHA,[lE]:n.ONE_MINUS_SRC_COLOR,[Ll]:n.ONE_MINUS_SRC_ALPHA,[fE]:n.ONE_MINUS_DST_COLOR,[uE]:n.ONE_MINUS_DST_ALPHA,[pE]:n.CONSTANT_COLOR,[mE]:n.ONE_MINUS_CONSTANT_COLOR,[gE]:n.CONSTANT_ALPHA,[_E]:n.ONE_MINUS_CONSTANT_ALPHA};function be(ce,Be,Te,Ve,Ye,Ue,nt,$e,It,yt){if(ce===Ri){g===!0&&(Me(n.BLEND),g=!1);return}if(g===!1&&(re(n.BLEND),g=!0),ce!==eE){if(ce!==_||yt!==k){if((O!==fr||B!==fr)&&(n.blendEquation(n.FUNC_ADD),O=fr,B=fr),yt)switch(ce){case na:n.blendFuncSeparate(n.ONE,n.ONE_MINUS_SRC_ALPHA,n.ONE,n.ONE_MINUS_SRC_ALPHA);break;case Fd:n.blendFunc(n.ONE,n.ONE);break;case Bd:n.blendFuncSeparate(n.ZERO,n.ONE_MINUS_SRC_COLOR,n.ZERO,n.ONE);break;case zd:n.blendFuncSeparate(n.DST_COLOR,n.ONE_MINUS_SRC_ALPHA,n.ZERO,n.ONE);break;default:Rt("WebGLState: Invalid blending: ",ce);break}else switch(ce){case na:n.blendFuncSeparate(n.SRC_ALPHA,n.ONE_MINUS_SRC_ALPHA,n.ONE,n.ONE_MINUS_SRC_ALPHA);break;case Fd:n.blendFuncSeparate(n.SRC_ALPHA,n.ONE,n.ONE,n.ONE);break;case Bd:Rt("WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case zd:Rt("WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:Rt("WebGLState: Invalid blending: ",ce);break}D=null,y=null,R=null,C=null,b.set(0,0,0),A=0,_=ce,k=yt}return}Ye=Ye||Be,Ue=Ue||Te,nt=nt||Ve,(Be!==O||Ye!==B)&&(n.blendEquationSeparate(ye[Be],ye[Ye]),O=Be,B=Ye),(Te!==D||Ve!==y||Ue!==R||nt!==C)&&(n.blendFuncSeparate(Ie[Te],Ie[Ve],Ie[Ue],Ie[nt]),D=Te,y=Ve,R=Ue,C=nt),($e.equals(b)===!1||It!==A)&&(n.blendColor($e.r,$e.g,$e.b,It),b.copy($e),A=It),_=ce,k=!1}function ke(ce,Be){ce.side===oi?Me(n.CULL_FACE):re(n.CULL_FACE);let Te=ce.side===yn;Be&&(Te=!Te),xe(Te),ce.blending===na&&ce.transparent===!1?be(Ri):be(ce.blending,ce.blendEquation,ce.blendSrc,ce.blendDst,ce.blendEquationAlpha,ce.blendSrcAlpha,ce.blendDstAlpha,ce.blendColor,ce.blendAlpha,ce.premultipliedAlpha),o.setFunc(ce.depthFunc),o.setTest(ce.depthTest),o.setMask(ce.depthWrite),a.setMask(ce.colorWrite);const Ve=ce.stencilWrite;l.setTest(Ve),Ve&&(l.setMask(ce.stencilWriteMask),l.setFunc(ce.stencilFunc,ce.stencilRef,ce.stencilFuncMask),l.setOp(ce.stencilFail,ce.stencilZFail,ce.stencilZPass)),De(ce.polygonOffset,ce.polygonOffsetFactor,ce.polygonOffsetUnits),ce.alphaToCoverage===!0?re(n.SAMPLE_ALPHA_TO_COVERAGE):Me(n.SAMPLE_ALPHA_TO_COVERAGE)}function xe(ce){z!==ce&&(ce?n.frontFace(n.CW):n.frontFace(n.CCW),z=ce)}function Ee(ce){ce!==Jy?(re(n.CULL_FACE),ce!==H&&(ce===Od?n.cullFace(n.BACK):ce===Qy?n.cullFace(n.FRONT):n.cullFace(n.FRONT_AND_BACK))):Me(n.CULL_FACE),H=ce}function _e(ce){ce!==q&&(w&&n.lineWidth(ce),q=ce)}function De(ce,Be,Te){ce?(re(n.POLYGON_OFFSET_FILL),(Q!==Be||G!==Te)&&(Q=Be,G=Te,o.getReversed()&&(Be=-Be),n.polygonOffset(Be,Te))):Me(n.POLYGON_OFFSET_FILL)}function Ne(ce){ce?re(n.SCISSOR_TEST):Me(n.SCISSOR_TEST)}function Oe(ce){ce===void 0&&(ce=n.TEXTURE0+T-1),Y!==ce&&(n.activeTexture(ce),Y=ce)}function J(ce,Be,Te){Te===void 0&&(Y===null?Te=n.TEXTURE0+T-1:Te=Y);let Ve=te[Te];Ve===void 0&&(Ve={type:void 0,texture:void 0},te[Te]=Ve),(Ve.type!==ce||Ve.texture!==Be)&&(Y!==Te&&(n.activeTexture(Te),Y=Te),n.bindTexture(ce,Be||V[ce]),Ve.type=ce,Ve.texture=Be)}function We(){const ce=te[Y];ce!==void 0&&ce.type!==void 0&&(n.bindTexture(ce.type,null),ce.type=void 0,ce.texture=void 0)}function Fe(){try{n.compressedTexImage2D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function P(){try{n.compressedTexImage3D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function x(){try{n.texSubImage2D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function Z(){try{n.texSubImage3D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function ae(){try{n.compressedTexSubImage2D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function de(){try{n.compressedTexSubImage3D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function Le(){try{n.texStorage2D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function He(){try{n.texStorage3D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function Se(){try{n.texImage2D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function we(){try{n.texImage3D(...arguments)}catch(ce){Rt("WebGLState:",ce)}}function Ge(ce){return h[ce]!==void 0?h[ce]:n.getParameter(ce)}function Je(ce,Be){h[ce]!==Be&&(n.pixelStorei(ce,Be),h[ce]=Be)}function Pe(ce){se.equals(ce)===!1&&(n.scissor(ce.x,ce.y,ce.z,ce.w),se.copy(ce))}function Ce(ce){ne.equals(ce)===!1&&(n.viewport(ce.x,ce.y,ce.z,ce.w),ne.copy(ce))}function qe(ce,Be){let Te=u.get(Be);Te===void 0&&(Te=new WeakMap,u.set(Be,Te));let Ve=Te.get(ce);Ve===void 0&&(Ve=n.getUniformBlockIndex(Be,ce.name),Te.set(ce,Ve))}function je(ce,Be){const Ve=u.get(Be).get(ce);c.get(Be)!==Ve&&(n.uniformBlockBinding(Be,Ve,ce.__bindingPointIndex),c.set(Be,Ve))}function st(){n.disable(n.BLEND),n.disable(n.CULL_FACE),n.disable(n.DEPTH_TEST),n.disable(n.POLYGON_OFFSET_FILL),n.disable(n.SCISSOR_TEST),n.disable(n.STENCIL_TEST),n.disable(n.SAMPLE_ALPHA_TO_COVERAGE),n.blendEquation(n.FUNC_ADD),n.blendFunc(n.ONE,n.ZERO),n.blendFuncSeparate(n.ONE,n.ZERO,n.ONE,n.ZERO),n.blendColor(0,0,0,0),n.colorMask(!0,!0,!0,!0),n.clearColor(0,0,0,0),n.depthMask(!0),n.depthFunc(n.LESS),o.setReversed(!1),n.clearDepth(1),n.stencilMask(4294967295),n.stencilFunc(n.ALWAYS,0,4294967295),n.stencilOp(n.KEEP,n.KEEP,n.KEEP),n.clearStencil(0),n.cullFace(n.BACK),n.frontFace(n.CCW),n.polygonOffset(0,0),n.activeTexture(n.TEXTURE0),n.bindFramebuffer(n.FRAMEBUFFER,null),n.bindFramebuffer(n.DRAW_FRAMEBUFFER,null),n.bindFramebuffer(n.READ_FRAMEBUFFER,null),n.useProgram(null),n.lineWidth(1),n.scissor(0,0,n.canvas.width,n.canvas.height),n.viewport(0,0,n.canvas.width,n.canvas.height),n.pixelStorei(n.PACK_ALIGNMENT,4),n.pixelStorei(n.UNPACK_ALIGNMENT,4),n.pixelStorei(n.UNPACK_FLIP_Y_WEBGL,!1),n.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL,!1),n.pixelStorei(n.UNPACK_COLORSPACE_CONVERSION_WEBGL,n.BROWSER_DEFAULT_WEBGL),n.pixelStorei(n.PACK_ROW_LENGTH,0),n.pixelStorei(n.PACK_SKIP_PIXELS,0),n.pixelStorei(n.PACK_SKIP_ROWS,0),n.pixelStorei(n.UNPACK_ROW_LENGTH,0),n.pixelStorei(n.UNPACK_IMAGE_HEIGHT,0),n.pixelStorei(n.UNPACK_SKIP_PIXELS,0),n.pixelStorei(n.UNPACK_SKIP_ROWS,0),n.pixelStorei(n.UNPACK_SKIP_IMAGES,0),f={},h={},Y=null,te={},d={},p=new WeakMap,m=[],E=null,g=!1,_=null,O=null,D=null,y=null,B=null,R=null,C=null,b=new Ct(0,0,0),A=0,k=!1,z=null,H=null,q=null,Q=null,G=null,se.set(0,0,n.canvas.width,n.canvas.height),ne.set(0,0,n.canvas.width,n.canvas.height),a.reset(),o.reset(),l.reset()}return{buffers:{color:a,depth:o,stencil:l},enable:re,disable:Me,bindFramebuffer:fe,drawBuffers:oe,useProgram:ve,setBlending:be,setMaterial:ke,setFlipSided:xe,setCullFace:Ee,setLineWidth:_e,setPolygonOffset:De,setScissorTest:Ne,activeTexture:Oe,bindTexture:J,unbindTexture:We,compressedTexImage2D:Fe,compressedTexImage3D:P,texImage2D:Se,texImage3D:we,pixelStorei:Je,getParameter:Ge,updateUBOMapping:qe,uniformBlockBinding:je,texStorage2D:Le,texStorage3D:He,texSubImage2D:x,texSubImage3D:Z,compressedTexSubImage2D:ae,compressedTexSubImage3D:de,scissor:Pe,viewport:Ce,reset:st}}function tR(n,e,t,i,r,a,o){const l=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),u=new xt,f=new WeakMap,h=new Set;let d;const p=new WeakMap;let m=!1;try{m=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function E(P,x){return m?new OffscreenCanvas(P,x):co("canvas")}function g(P,x,Z){let ae=1;const de=Fe(P);if((de.width>Z||de.height>Z)&&(ae=Z/Math.max(de.width,de.height)),ae<1)if(typeof HTMLImageElement<"u"&&P instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&P instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&P instanceof ImageBitmap||typeof VideoFrame<"u"&&P instanceof VideoFrame){const Le=Math.floor(ae*de.width),He=Math.floor(ae*de.height);d===void 0&&(d=E(Le,He));const Se=x?E(Le,He):d;return Se.width=Le,Se.height=He,Se.getContext("2d").drawImage(P,0,0,Le,He),ut("WebGLRenderer: Texture has been resized from ("+de.width+"x"+de.height+") to ("+Le+"x"+He+")."),Se}else return"data"in P&&ut("WebGLRenderer: Image in DataTexture is too big ("+de.width+"x"+de.height+")."),P;return P}function _(P){return P.generateMipmaps}function O(P){n.generateMipmap(P)}function D(P){return P.isWebGLCubeRenderTarget?n.TEXTURE_CUBE_MAP:P.isWebGL3DRenderTarget?n.TEXTURE_3D:P.isWebGLArrayRenderTarget||P.isCompressedArrayTexture?n.TEXTURE_2D_ARRAY:n.TEXTURE_2D}function y(P,x,Z,ae,de,Le=!1){if(P!==null){if(n[P]!==void 0)return n[P];ut("WebGLRenderer: Attempt to use non-existing WebGL internal format '"+P+"'")}let He;ae&&(He=e.get("EXT_texture_norm16"),He||ut("WebGLRenderer: Unable to use normalized textures without EXT_texture_norm16 extension"));let Se=x;if(x===n.RED&&(Z===n.FLOAT&&(Se=n.R32F),Z===n.HALF_FLOAT&&(Se=n.R16F),Z===n.UNSIGNED_BYTE&&(Se=n.R8),Z===n.UNSIGNED_SHORT&&He&&(Se=He.R16_EXT),Z===n.SHORT&&He&&(Se=He.R16_SNORM_EXT)),x===n.RED_INTEGER&&(Z===n.UNSIGNED_BYTE&&(Se=n.R8UI),Z===n.UNSIGNED_SHORT&&(Se=n.R16UI),Z===n.UNSIGNED_INT&&(Se=n.R32UI),Z===n.BYTE&&(Se=n.R8I),Z===n.SHORT&&(Se=n.R16I),Z===n.INT&&(Se=n.R32I)),x===n.RG&&(Z===n.FLOAT&&(Se=n.RG32F),Z===n.HALF_FLOAT&&(Se=n.RG16F),Z===n.UNSIGNED_BYTE&&(Se=n.RG8),Z===n.UNSIGNED_SHORT&&He&&(Se=He.RG16_EXT),Z===n.SHORT&&He&&(Se=He.RG16_SNORM_EXT)),x===n.RG_INTEGER&&(Z===n.UNSIGNED_BYTE&&(Se=n.RG8UI),Z===n.UNSIGNED_SHORT&&(Se=n.RG16UI),Z===n.UNSIGNED_INT&&(Se=n.RG32UI),Z===n.BYTE&&(Se=n.RG8I),Z===n.SHORT&&(Se=n.RG16I),Z===n.INT&&(Se=n.RG32I)),x===n.RGB_INTEGER&&(Z===n.UNSIGNED_BYTE&&(Se=n.RGB8UI),Z===n.UNSIGNED_SHORT&&(Se=n.RGB16UI),Z===n.UNSIGNED_INT&&(Se=n.RGB32UI),Z===n.BYTE&&(Se=n.RGB8I),Z===n.SHORT&&(Se=n.RGB16I),Z===n.INT&&(Se=n.RGB32I)),x===n.RGBA_INTEGER&&(Z===n.UNSIGNED_BYTE&&(Se=n.RGBA8UI),Z===n.UNSIGNED_SHORT&&(Se=n.RGBA16UI),Z===n.UNSIGNED_INT&&(Se=n.RGBA32UI),Z===n.BYTE&&(Se=n.RGBA8I),Z===n.SHORT&&(Se=n.RGBA16I),Z===n.INT&&(Se=n.RGBA32I)),x===n.RGB&&(Z===n.UNSIGNED_SHORT&&He&&(Se=He.RGB16_EXT),Z===n.SHORT&&He&&(Se=He.RGB16_SNORM_EXT),Z===n.UNSIGNED_INT_5_9_9_9_REV&&(Se=n.RGB9_E5),Z===n.UNSIGNED_INT_10F_11F_11F_REV&&(Se=n.R11F_G11F_B10F)),x===n.RGBA){const we=Le?lo:bt.getTransfer(de);Z===n.FLOAT&&(Se=n.RGBA32F),Z===n.HALF_FLOAT&&(Se=n.RGBA16F),Z===n.UNSIGNED_BYTE&&(Se=we===Nt?n.SRGB8_ALPHA8:n.RGBA8),Z===n.UNSIGNED_SHORT&&He&&(Se=He.RGBA16_EXT),Z===n.SHORT&&He&&(Se=He.RGBA16_SNORM_EXT),Z===n.UNSIGNED_SHORT_4_4_4_4&&(Se=n.RGBA4),Z===n.UNSIGNED_SHORT_5_5_5_1&&(Se=n.RGB5_A1)}return(Se===n.R16F||Se===n.R32F||Se===n.RG16F||Se===n.RG32F||Se===n.RGBA16F||Se===n.RGBA32F)&&e.get("EXT_color_buffer_float"),Se}function B(P,x){let Z;return P?x===null||x===mi||x===Ja?Z=n.DEPTH24_STENCIL8:x===ci?Z=n.DEPTH32F_STENCIL8:x===Za&&(Z=n.DEPTH24_STENCIL8,ut("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):x===null||x===mi||x===Ja?Z=n.DEPTH_COMPONENT24:x===ci?Z=n.DEPTH_COMPONENT32F:x===Za&&(Z=n.DEPTH_COMPONENT16),Z}function R(P,x){return _(P)===!0||P.isFramebufferTexture&&P.minFilter!==an&&P.minFilter!==fn?Math.log2(Math.max(x.width,x.height))+1:P.mipmaps!==void 0&&P.mipmaps.length>0?P.mipmaps.length:P.isCompressedTexture&&Array.isArray(P.image)?x.mipmaps.length:1}function C(P){const x=P.target;x.removeEventListener("dispose",C),A(x),x.isVideoTexture&&f.delete(x),x.isHTMLTexture&&h.delete(x)}function b(P){const x=P.target;x.removeEventListener("dispose",b),z(x)}function A(P){const x=i.get(P);if(x.__webglInit===void 0)return;const Z=P.source,ae=p.get(Z);if(ae){const de=ae[x.__cacheKey];de.usedTimes--,de.usedTimes===0&&k(P),Object.keys(ae).length===0&&p.delete(Z)}i.remove(P)}function k(P){const x=i.get(P);n.deleteTexture(x.__webglTexture);const Z=P.source,ae=p.get(Z);delete ae[x.__cacheKey],o.memory.textures--}function z(P){const x=i.get(P);if(P.depthTexture&&(P.depthTexture.dispose(),i.remove(P.depthTexture)),P.isWebGLCubeRenderTarget)for(let ae=0;ae<6;ae++){if(Array.isArray(x.__webglFramebuffer[ae]))for(let de=0;de<x.__webglFramebuffer[ae].length;de++)n.deleteFramebuffer(x.__webglFramebuffer[ae][de]);else n.deleteFramebuffer(x.__webglFramebuffer[ae]);x.__webglDepthbuffer&&n.deleteRenderbuffer(x.__webglDepthbuffer[ae])}else{if(Array.isArray(x.__webglFramebuffer))for(let ae=0;ae<x.__webglFramebuffer.length;ae++)n.deleteFramebuffer(x.__webglFramebuffer[ae]);else n.deleteFramebuffer(x.__webglFramebuffer);if(x.__webglDepthbuffer&&n.deleteRenderbuffer(x.__webglDepthbuffer),x.__webglMultisampledFramebuffer&&n.deleteFramebuffer(x.__webglMultisampledFramebuffer),x.__webglColorRenderbuffer)for(let ae=0;ae<x.__webglColorRenderbuffer.length;ae++)x.__webglColorRenderbuffer[ae]&&n.deleteRenderbuffer(x.__webglColorRenderbuffer[ae]);x.__webglDepthRenderbuffer&&n.deleteRenderbuffer(x.__webglDepthRenderbuffer)}const Z=P.textures;for(let ae=0,de=Z.length;ae<de;ae++){const Le=i.get(Z[ae]);Le.__webglTexture&&(n.deleteTexture(Le.__webglTexture),o.memory.textures--),i.remove(Z[ae])}i.remove(P)}let H=0;function q(){H=0}function Q(){return H}function G(P){H=P}function T(){const P=H;return P>=r.maxTextures&&ut("WebGLTextures: Trying to use "+P+" texture units while this GPU supports only "+r.maxTextures),H+=1,P}function w(P){const x=[];return x.push(P.wrapS),x.push(P.wrapT),x.push(P.wrapR||0),x.push(P.magFilter),x.push(P.minFilter),x.push(P.anisotropy),x.push(P.internalFormat),x.push(P.format),x.push(P.type),x.push(P.generateMipmaps),x.push(P.premultiplyAlpha),x.push(P.flipY),x.push(P.unpackAlignment),x.push(P.colorSpace),x.join()}function I(P,x){const Z=i.get(P);if(P.isVideoTexture&&J(P),P.isRenderTargetTexture===!1&&P.isExternalTexture!==!0&&P.version>0&&Z.__version!==P.version){const ae=P.image;if(ae===null)ut("WebGLRenderer: Texture marked for update but no image data found.");else if(ae.complete===!1)ut("WebGLRenderer: Texture marked for update but image is incomplete");else{Me(Z,P,x);return}}else P.isExternalTexture&&(Z.__webglTexture=P.sourceTexture?P.sourceTexture:null);t.bindTexture(n.TEXTURE_2D,Z.__webglTexture,n.TEXTURE0+x)}function F(P,x){const Z=i.get(P);if(P.isRenderTargetTexture===!1&&P.version>0&&Z.__version!==P.version){Me(Z,P,x);return}else P.isExternalTexture&&(Z.__webglTexture=P.sourceTexture?P.sourceTexture:null);t.bindTexture(n.TEXTURE_2D_ARRAY,Z.__webglTexture,n.TEXTURE0+x)}function Y(P,x){const Z=i.get(P);if(P.isRenderTargetTexture===!1&&P.version>0&&Z.__version!==P.version){Me(Z,P,x);return}t.bindTexture(n.TEXTURE_3D,Z.__webglTexture,n.TEXTURE0+x)}function te(P,x){const Z=i.get(P);if(P.isCubeDepthTexture!==!0&&P.version>0&&Z.__version!==P.version){fe(Z,P,x);return}t.bindTexture(n.TEXTURE_CUBE_MAP,Z.__webglTexture,n.TEXTURE0+x)}const X={[Hl]:n.REPEAT,[wi]:n.CLAMP_TO_EDGE,[Gl]:n.MIRRORED_REPEAT},K={[an]:n.NEAREST,[bE]:n.NEAREST_MIPMAP_NEAREST,[xs]:n.NEAREST_MIPMAP_LINEAR,[fn]:n.LINEAR,[Go]:n.LINEAR_MIPMAP_NEAREST,[pr]:n.LINEAR_MIPMAP_LINEAR},se={[EE]:n.NEVER,[RE]:n.ALWAYS,[ME]:n.LESS,[bu]:n.LEQUAL,[TE]:n.EQUAL,[Su]:n.GEQUAL,[wE]:n.GREATER,[AE]:n.NOTEQUAL};function ne(P,x){if(x.type===ci&&e.has("OES_texture_float_linear")===!1&&(x.magFilter===fn||x.magFilter===Go||x.magFilter===xs||x.magFilter===pr||x.minFilter===fn||x.minFilter===Go||x.minFilter===xs||x.minFilter===pr)&&ut("WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),n.texParameteri(P,n.TEXTURE_WRAP_S,X[x.wrapS]),n.texParameteri(P,n.TEXTURE_WRAP_T,X[x.wrapT]),(P===n.TEXTURE_3D||P===n.TEXTURE_2D_ARRAY)&&n.texParameteri(P,n.TEXTURE_WRAP_R,X[x.wrapR]),n.texParameteri(P,n.TEXTURE_MAG_FILTER,K[x.magFilter]),n.texParameteri(P,n.TEXTURE_MIN_FILTER,K[x.minFilter]),x.compareFunction&&(n.texParameteri(P,n.TEXTURE_COMPARE_MODE,n.COMPARE_REF_TO_TEXTURE),n.texParameteri(P,n.TEXTURE_COMPARE_FUNC,se[x.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(x.magFilter===an||x.minFilter!==xs&&x.minFilter!==pr||x.type===ci&&e.has("OES_texture_float_linear")===!1)return;if(x.anisotropy>1||i.get(x).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");n.texParameterf(P,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(x.anisotropy,r.getMaxAnisotropy())),i.get(x).__currentAnisotropy=x.anisotropy}}}function N(P,x){let Z=!1;P.__webglInit===void 0&&(P.__webglInit=!0,x.addEventListener("dispose",C));const ae=x.source;let de=p.get(ae);de===void 0&&(de={},p.set(ae,de));const Le=w(x);if(Le!==P.__cacheKey){de[Le]===void 0&&(de[Le]={texture:n.createTexture(),usedTimes:0},o.memory.textures++,Z=!0),de[Le].usedTimes++;const He=de[P.__cacheKey];He!==void 0&&(de[P.__cacheKey].usedTimes--,He.usedTimes===0&&k(x)),P.__cacheKey=Le,P.__webglTexture=de[Le].texture}return Z}function V(P,x,Z){return Math.floor(Math.floor(P/Z)/x)}function re(P,x,Z,ae){const Le=P.updateRanges;if(Le.length===0)t.texSubImage2D(n.TEXTURE_2D,0,0,0,x.width,x.height,Z,ae,x.data);else{Le.sort((Je,Pe)=>Je.start-Pe.start);let He=0;for(let Je=1;Je<Le.length;Je++){const Pe=Le[He],Ce=Le[Je],qe=Pe.start+Pe.count,je=V(Ce.start,x.width,4),st=V(Pe.start,x.width,4);Ce.start<=qe+1&&je===st&&V(Ce.start+Ce.count-1,x.width,4)===je?Pe.count=Math.max(Pe.count,Ce.start+Ce.count-Pe.start):(++He,Le[He]=Ce)}Le.length=He+1;const Se=t.getParameter(n.UNPACK_ROW_LENGTH),we=t.getParameter(n.UNPACK_SKIP_PIXELS),Ge=t.getParameter(n.UNPACK_SKIP_ROWS);t.pixelStorei(n.UNPACK_ROW_LENGTH,x.width);for(let Je=0,Pe=Le.length;Je<Pe;Je++){const Ce=Le[Je],qe=Math.floor(Ce.start/4),je=Math.ceil(Ce.count/4),st=qe%x.width,ce=Math.floor(qe/x.width),Be=je,Te=1;t.pixelStorei(n.UNPACK_SKIP_PIXELS,st),t.pixelStorei(n.UNPACK_SKIP_ROWS,ce),t.texSubImage2D(n.TEXTURE_2D,0,st,ce,Be,Te,Z,ae,x.data)}P.clearUpdateRanges(),t.pixelStorei(n.UNPACK_ROW_LENGTH,Se),t.pixelStorei(n.UNPACK_SKIP_PIXELS,we),t.pixelStorei(n.UNPACK_SKIP_ROWS,Ge)}}function Me(P,x,Z){let ae=n.TEXTURE_2D;(x.isDataArrayTexture||x.isCompressedArrayTexture)&&(ae=n.TEXTURE_2D_ARRAY),x.isData3DTexture&&(ae=n.TEXTURE_3D);const de=N(P,x),Le=x.source;t.bindTexture(ae,P.__webglTexture,n.TEXTURE0+Z);const He=i.get(Le);if(Le.version!==He.__version||de===!0){if(t.activeTexture(n.TEXTURE0+Z),(typeof ImageBitmap<"u"&&x.image instanceof ImageBitmap)===!1){const Te=bt.getPrimaries(bt.workingColorSpace),Ve=x.colorSpace===Ji?null:bt.getPrimaries(x.colorSpace),Ye=x.colorSpace===Ji||Te===Ve?n.NONE:n.BROWSER_DEFAULT_WEBGL;t.pixelStorei(n.UNPACK_FLIP_Y_WEBGL,x.flipY),t.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL,x.premultiplyAlpha),t.pixelStorei(n.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ye)}t.pixelStorei(n.UNPACK_ALIGNMENT,x.unpackAlignment);let we=g(x.image,!1,r.maxTextureSize);we=We(x,we);const Ge=a.convert(x.format,x.colorSpace),Je=a.convert(x.type);let Pe=y(x.internalFormat,Ge,Je,x.normalized,x.colorSpace,x.isVideoTexture);ne(ae,x);let Ce;const qe=x.mipmaps,je=x.isVideoTexture!==!0,st=He.__version===void 0||de===!0,ce=Le.dataReady,Be=R(x,we);if(x.isDepthTexture)Pe=B(x.format===mr,x.type),st&&(je?t.texStorage2D(n.TEXTURE_2D,1,Pe,we.width,we.height):t.texImage2D(n.TEXTURE_2D,0,Pe,we.width,we.height,0,Ge,Je,null));else if(x.isDataTexture)if(qe.length>0){je&&st&&t.texStorage2D(n.TEXTURE_2D,Be,Pe,qe[0].width,qe[0].height);for(let Te=0,Ve=qe.length;Te<Ve;Te++)Ce=qe[Te],je?ce&&t.texSubImage2D(n.TEXTURE_2D,Te,0,0,Ce.width,Ce.height,Ge,Je,Ce.data):t.texImage2D(n.TEXTURE_2D,Te,Pe,Ce.width,Ce.height,0,Ge,Je,Ce.data);x.generateMipmaps=!1}else je?(st&&t.texStorage2D(n.TEXTURE_2D,Be,Pe,we.width,we.height),ce&&re(x,we,Ge,Je)):t.texImage2D(n.TEXTURE_2D,0,Pe,we.width,we.height,0,Ge,Je,we.data);else if(x.isCompressedTexture)if(x.isCompressedArrayTexture){je&&st&&t.texStorage3D(n.TEXTURE_2D_ARRAY,Be,Pe,qe[0].width,qe[0].height,we.depth);for(let Te=0,Ve=qe.length;Te<Ve;Te++)if(Ce=qe[Te],x.format!==Xn)if(Ge!==null)if(je){if(ce)if(x.layerUpdates.size>0){const Ye=mf(Ce.width,Ce.height,x.format,x.type);for(const Ue of x.layerUpdates){const nt=Ce.data.subarray(Ue*Ye/Ce.data.BYTES_PER_ELEMENT,(Ue+1)*Ye/Ce.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(n.TEXTURE_2D_ARRAY,Te,0,0,Ue,Ce.width,Ce.height,1,Ge,nt)}x.clearLayerUpdates()}else t.compressedTexSubImage3D(n.TEXTURE_2D_ARRAY,Te,0,0,0,Ce.width,Ce.height,we.depth,Ge,Ce.data)}else t.compressedTexImage3D(n.TEXTURE_2D_ARRAY,Te,Pe,Ce.width,Ce.height,we.depth,0,Ce.data,0,0);else ut("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else je?ce&&t.texSubImage3D(n.TEXTURE_2D_ARRAY,Te,0,0,0,Ce.width,Ce.height,we.depth,Ge,Je,Ce.data):t.texImage3D(n.TEXTURE_2D_ARRAY,Te,Pe,Ce.width,Ce.height,we.depth,0,Ge,Je,Ce.data)}else{je&&st&&t.texStorage2D(n.TEXTURE_2D,Be,Pe,qe[0].width,qe[0].height);for(let Te=0,Ve=qe.length;Te<Ve;Te++)Ce=qe[Te],x.format!==Xn?Ge!==null?je?ce&&t.compressedTexSubImage2D(n.TEXTURE_2D,Te,0,0,Ce.width,Ce.height,Ge,Ce.data):t.compressedTexImage2D(n.TEXTURE_2D,Te,Pe,Ce.width,Ce.height,0,Ce.data):ut("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):je?ce&&t.texSubImage2D(n.TEXTURE_2D,Te,0,0,Ce.width,Ce.height,Ge,Je,Ce.data):t.texImage2D(n.TEXTURE_2D,Te,Pe,Ce.width,Ce.height,0,Ge,Je,Ce.data)}else if(x.isDataArrayTexture)if(je){if(st&&t.texStorage3D(n.TEXTURE_2D_ARRAY,Be,Pe,we.width,we.height,we.depth),ce)if(x.layerUpdates.size>0){const Te=mf(we.width,we.height,x.format,x.type);for(const Ve of x.layerUpdates){const Ye=we.data.subarray(Ve*Te/we.data.BYTES_PER_ELEMENT,(Ve+1)*Te/we.data.BYTES_PER_ELEMENT);t.texSubImage3D(n.TEXTURE_2D_ARRAY,0,0,0,Ve,we.width,we.height,1,Ge,Je,Ye)}x.clearLayerUpdates()}else t.texSubImage3D(n.TEXTURE_2D_ARRAY,0,0,0,0,we.width,we.height,we.depth,Ge,Je,we.data)}else t.texImage3D(n.TEXTURE_2D_ARRAY,0,Pe,we.width,we.height,we.depth,0,Ge,Je,we.data);else if(x.isData3DTexture)je?(st&&t.texStorage3D(n.TEXTURE_3D,Be,Pe,we.width,we.height,we.depth),ce&&t.texSubImage3D(n.TEXTURE_3D,0,0,0,0,we.width,we.height,we.depth,Ge,Je,we.data)):t.texImage3D(n.TEXTURE_3D,0,Pe,we.width,we.height,we.depth,0,Ge,Je,we.data);else if(x.isFramebufferTexture){if(st)if(je)t.texStorage2D(n.TEXTURE_2D,Be,Pe,we.width,we.height);else{let Te=we.width,Ve=we.height;for(let Ye=0;Ye<Be;Ye++)t.texImage2D(n.TEXTURE_2D,Ye,Pe,Te,Ve,0,Ge,Je,null),Te>>=1,Ve>>=1}}else if(x.isHTMLTexture){if("texElementImage2D"in n){const Te=n.canvas;if(Te.hasAttribute("layoutsubtree")||Te.setAttribute("layoutsubtree","true"),we.parentNode!==Te){Te.appendChild(we),h.add(x),Te.onpaint=Ve=>{const Ye=Ve.changedElements;for(const Ue of h)Ye.includes(Ue.image)&&(Ue.needsUpdate=!0)},Te.requestPaint();return}if(n.texElementImage2D.length===3)n.texElementImage2D(n.TEXTURE_2D,n.RGBA8,we);else{const Ye=n.RGBA,Ue=n.RGBA,nt=n.UNSIGNED_BYTE;n.texElementImage2D(n.TEXTURE_2D,0,Ye,Ue,nt,we)}n.texParameteri(n.TEXTURE_2D,n.TEXTURE_MIN_FILTER,n.LINEAR),n.texParameteri(n.TEXTURE_2D,n.TEXTURE_WRAP_S,n.CLAMP_TO_EDGE),n.texParameteri(n.TEXTURE_2D,n.TEXTURE_WRAP_T,n.CLAMP_TO_EDGE)}}else if(qe.length>0){if(je&&st){const Te=Fe(qe[0]);t.texStorage2D(n.TEXTURE_2D,Be,Pe,Te.width,Te.height)}for(let Te=0,Ve=qe.length;Te<Ve;Te++)Ce=qe[Te],je?ce&&t.texSubImage2D(n.TEXTURE_2D,Te,0,0,Ge,Je,Ce):t.texImage2D(n.TEXTURE_2D,Te,Pe,Ge,Je,Ce);x.generateMipmaps=!1}else if(je){if(st){const Te=Fe(we);t.texStorage2D(n.TEXTURE_2D,Be,Pe,Te.width,Te.height)}ce&&t.texSubImage2D(n.TEXTURE_2D,0,0,0,Ge,Je,we)}else t.texImage2D(n.TEXTURE_2D,0,Pe,Ge,Je,we);_(x)&&O(ae),He.__version=Le.version,x.onUpdate&&x.onUpdate(x)}P.__version=x.version}function fe(P,x,Z){if(x.image.length!==6)return;const ae=N(P,x),de=x.source;t.bindTexture(n.TEXTURE_CUBE_MAP,P.__webglTexture,n.TEXTURE0+Z);const Le=i.get(de);if(de.version!==Le.__version||ae===!0){t.activeTexture(n.TEXTURE0+Z);const He=bt.getPrimaries(bt.workingColorSpace),Se=x.colorSpace===Ji?null:bt.getPrimaries(x.colorSpace),we=x.colorSpace===Ji||He===Se?n.NONE:n.BROWSER_DEFAULT_WEBGL;t.pixelStorei(n.UNPACK_FLIP_Y_WEBGL,x.flipY),t.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL,x.premultiplyAlpha),t.pixelStorei(n.UNPACK_ALIGNMENT,x.unpackAlignment),t.pixelStorei(n.UNPACK_COLORSPACE_CONVERSION_WEBGL,we);const Ge=x.isCompressedTexture||x.image[0].isCompressedTexture,Je=x.image[0]&&x.image[0].isDataTexture,Pe=[];for(let Ue=0;Ue<6;Ue++)!Ge&&!Je?Pe[Ue]=g(x.image[Ue],!0,r.maxCubemapSize):Pe[Ue]=Je?x.image[Ue].image:x.image[Ue],Pe[Ue]=We(x,Pe[Ue]);const Ce=Pe[0],qe=a.convert(x.format,x.colorSpace),je=a.convert(x.type),st=y(x.internalFormat,qe,je,x.normalized,x.colorSpace),ce=x.isVideoTexture!==!0,Be=Le.__version===void 0||ae===!0,Te=de.dataReady;let Ve=R(x,Ce);ne(n.TEXTURE_CUBE_MAP,x);let Ye;if(Ge){ce&&Be&&t.texStorage2D(n.TEXTURE_CUBE_MAP,Ve,st,Ce.width,Ce.height);for(let Ue=0;Ue<6;Ue++){Ye=Pe[Ue].mipmaps;for(let nt=0;nt<Ye.length;nt++){const $e=Ye[nt];x.format!==Xn?qe!==null?ce?Te&&t.compressedTexSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt,0,0,$e.width,$e.height,qe,$e.data):t.compressedTexImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt,st,$e.width,$e.height,0,$e.data):ut("WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):ce?Te&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt,0,0,$e.width,$e.height,qe,je,$e.data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt,st,$e.width,$e.height,0,qe,je,$e.data)}}}else{if(Ye=x.mipmaps,ce&&Be){Ye.length>0&&Ve++;const Ue=Fe(Pe[0]);t.texStorage2D(n.TEXTURE_CUBE_MAP,Ve,st,Ue.width,Ue.height)}for(let Ue=0;Ue<6;Ue++)if(Je){ce?Te&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,0,0,0,Pe[Ue].width,Pe[Ue].height,qe,je,Pe[Ue].data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,0,st,Pe[Ue].width,Pe[Ue].height,0,qe,je,Pe[Ue].data);for(let nt=0;nt<Ye.length;nt++){const It=Ye[nt].image[Ue].image;ce?Te&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt+1,0,0,It.width,It.height,qe,je,It.data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt+1,st,It.width,It.height,0,qe,je,It.data)}}else{ce?Te&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,0,0,0,qe,je,Pe[Ue]):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,0,st,qe,je,Pe[Ue]);for(let nt=0;nt<Ye.length;nt++){const $e=Ye[nt];ce?Te&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt+1,0,0,qe,je,$e.image[Ue]):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ue,nt+1,st,qe,je,$e.image[Ue])}}}_(x)&&O(n.TEXTURE_CUBE_MAP),Le.__version=de.version,x.onUpdate&&x.onUpdate(x)}P.__version=x.version}function oe(P,x,Z,ae,de,Le){const He=a.convert(Z.format,Z.colorSpace),Se=a.convert(Z.type),we=y(Z.internalFormat,He,Se,Z.normalized,Z.colorSpace),Ge=i.get(x),Je=i.get(Z);if(Je.__renderTarget=x,!Ge.__hasExternalTextures){const Pe=Math.max(1,x.width>>Le),Ce=Math.max(1,x.height>>Le);de===n.TEXTURE_3D||de===n.TEXTURE_2D_ARRAY?t.texImage3D(de,Le,we,Pe,Ce,x.depth,0,He,Se,null):t.texImage2D(de,Le,we,Pe,Ce,0,He,Se,null)}t.bindFramebuffer(n.FRAMEBUFFER,P),Oe(x)?l.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,ae,de,Je.__webglTexture,0,Ne(x)):(de===n.TEXTURE_2D||de>=n.TEXTURE_CUBE_MAP_POSITIVE_X&&de<=n.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&n.framebufferTexture2D(n.FRAMEBUFFER,ae,de,Je.__webglTexture,Le),t.bindFramebuffer(n.FRAMEBUFFER,null)}function ve(P,x,Z){if(n.bindRenderbuffer(n.RENDERBUFFER,P),x.depthBuffer){const ae=x.depthTexture,de=ae&&ae.isDepthTexture?ae.type:null,Le=B(x.stencilBuffer,de),He=x.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT;Oe(x)?l.renderbufferStorageMultisampleEXT(n.RENDERBUFFER,Ne(x),Le,x.width,x.height):Z?n.renderbufferStorageMultisample(n.RENDERBUFFER,Ne(x),Le,x.width,x.height):n.renderbufferStorage(n.RENDERBUFFER,Le,x.width,x.height),n.framebufferRenderbuffer(n.FRAMEBUFFER,He,n.RENDERBUFFER,P)}else{const ae=x.textures;for(let de=0;de<ae.length;de++){const Le=ae[de],He=a.convert(Le.format,Le.colorSpace),Se=a.convert(Le.type),we=y(Le.internalFormat,He,Se,Le.normalized,Le.colorSpace);Oe(x)?l.renderbufferStorageMultisampleEXT(n.RENDERBUFFER,Ne(x),we,x.width,x.height):Z?n.renderbufferStorageMultisample(n.RENDERBUFFER,Ne(x),we,x.width,x.height):n.renderbufferStorage(n.RENDERBUFFER,we,x.width,x.height)}}n.bindRenderbuffer(n.RENDERBUFFER,null)}function ye(P,x,Z){const ae=x.isWebGLCubeRenderTarget===!0;if(t.bindFramebuffer(n.FRAMEBUFFER,P),!(x.depthTexture&&x.depthTexture.isDepthTexture))throw new Error("THREE.WebGLTextures: renderTarget.depthTexture must be an instance of THREE.DepthTexture.");const de=i.get(x.depthTexture);if(de.__renderTarget=x,(!de.__webglTexture||x.depthTexture.image.width!==x.width||x.depthTexture.image.height!==x.height)&&(x.depthTexture.image.width=x.width,x.depthTexture.image.height=x.height,x.depthTexture.needsUpdate=!0),ae){if(de.__webglInit===void 0&&(de.__webglInit=!0,x.depthTexture.addEventListener("dispose",C)),de.__webglTexture===void 0){de.__webglTexture=n.createTexture(),t.bindTexture(n.TEXTURE_CUBE_MAP,de.__webglTexture),ne(n.TEXTURE_CUBE_MAP,x.depthTexture);const Ge=a.convert(x.depthTexture.format),Je=a.convert(x.depthTexture.type);let Pe;x.depthTexture.format===Ui?Pe=n.DEPTH_COMPONENT24:x.depthTexture.format===mr&&(Pe=n.DEPTH24_STENCIL8);for(let Ce=0;Ce<6;Ce++)n.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+Ce,0,Pe,x.width,x.height,0,Ge,Je,null)}}else I(x.depthTexture,0);const Le=de.__webglTexture,He=Ne(x),Se=ae?n.TEXTURE_CUBE_MAP_POSITIVE_X+Z:n.TEXTURE_2D,we=x.depthTexture.format===mr?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT;if(x.depthTexture.format===Ui)Oe(x)?l.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,we,Se,Le,0,He):n.framebufferTexture2D(n.FRAMEBUFFER,we,Se,Le,0);else if(x.depthTexture.format===mr)Oe(x)?l.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,we,Se,Le,0,He):n.framebufferTexture2D(n.FRAMEBUFFER,we,Se,Le,0);else throw new Error("THREE.WebGLTextures: Unknown depthTexture format.")}function Ie(P){const x=i.get(P),Z=P.isWebGLCubeRenderTarget===!0;if(x.__boundDepthTexture!==P.depthTexture){const ae=P.depthTexture;if(x.__depthDisposeCallback&&x.__depthDisposeCallback(),ae){const de=()=>{delete x.__boundDepthTexture,delete x.__depthDisposeCallback,ae.removeEventListener("dispose",de)};ae.addEventListener("dispose",de),x.__depthDisposeCallback=de}x.__boundDepthTexture=ae}if(P.depthTexture&&!x.__autoAllocateDepthBuffer)if(Z)for(let ae=0;ae<6;ae++)ye(x.__webglFramebuffer[ae],P,ae);else{const ae=P.texture.mipmaps;ae&&ae.length>0?ye(x.__webglFramebuffer[0],P,0):ye(x.__webglFramebuffer,P,0)}else if(Z){x.__webglDepthbuffer=[];for(let ae=0;ae<6;ae++)if(t.bindFramebuffer(n.FRAMEBUFFER,x.__webglFramebuffer[ae]),x.__webglDepthbuffer[ae]===void 0)x.__webglDepthbuffer[ae]=n.createRenderbuffer(),ve(x.__webglDepthbuffer[ae],P,!1);else{const de=P.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,Le=x.__webglDepthbuffer[ae];n.bindRenderbuffer(n.RENDERBUFFER,Le),n.framebufferRenderbuffer(n.FRAMEBUFFER,de,n.RENDERBUFFER,Le)}}else{const ae=P.texture.mipmaps;if(ae&&ae.length>0?t.bindFramebuffer(n.FRAMEBUFFER,x.__webglFramebuffer[0]):t.bindFramebuffer(n.FRAMEBUFFER,x.__webglFramebuffer),x.__webglDepthbuffer===void 0)x.__webglDepthbuffer=n.createRenderbuffer(),ve(x.__webglDepthbuffer,P,!1);else{const de=P.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,Le=x.__webglDepthbuffer;n.bindRenderbuffer(n.RENDERBUFFER,Le),n.framebufferRenderbuffer(n.FRAMEBUFFER,de,n.RENDERBUFFER,Le)}}t.bindFramebuffer(n.FRAMEBUFFER,null)}function be(P,x,Z){const ae=i.get(P);x!==void 0&&oe(ae.__webglFramebuffer,P,P.texture,n.COLOR_ATTACHMENT0,n.TEXTURE_2D,0),Z!==void 0&&Ie(P)}function ke(P){const x=P.texture,Z=i.get(P),ae=i.get(x);P.addEventListener("dispose",b);const de=P.textures,Le=P.isWebGLCubeRenderTarget===!0,He=de.length>1;if(He||(ae.__webglTexture===void 0&&(ae.__webglTexture=n.createTexture()),ae.__version=x.version,o.memory.textures++),Le){Z.__webglFramebuffer=[];for(let Se=0;Se<6;Se++)if(x.mipmaps&&x.mipmaps.length>0){Z.__webglFramebuffer[Se]=[];for(let we=0;we<x.mipmaps.length;we++)Z.__webglFramebuffer[Se][we]=n.createFramebuffer()}else Z.__webglFramebuffer[Se]=n.createFramebuffer()}else{if(x.mipmaps&&x.mipmaps.length>0){Z.__webglFramebuffer=[];for(let Se=0;Se<x.mipmaps.length;Se++)Z.__webglFramebuffer[Se]=n.createFramebuffer()}else Z.__webglFramebuffer=n.createFramebuffer();if(He)for(let Se=0,we=de.length;Se<we;Se++){const Ge=i.get(de[Se]);Ge.__webglTexture===void 0&&(Ge.__webglTexture=n.createTexture(),o.memory.textures++)}if(P.samples>0&&Oe(P)===!1){Z.__webglMultisampledFramebuffer=n.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(n.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let Se=0;Se<de.length;Se++){const we=de[Se];Z.__webglColorRenderbuffer[Se]=n.createRenderbuffer(),n.bindRenderbuffer(n.RENDERBUFFER,Z.__webglColorRenderbuffer[Se]);const Ge=a.convert(we.format,we.colorSpace),Je=a.convert(we.type),Pe=y(we.internalFormat,Ge,Je,we.normalized,we.colorSpace,P.isXRRenderTarget===!0),Ce=Ne(P);n.renderbufferStorageMultisample(n.RENDERBUFFER,Ce,Pe,P.width,P.height),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+Se,n.RENDERBUFFER,Z.__webglColorRenderbuffer[Se])}n.bindRenderbuffer(n.RENDERBUFFER,null),P.depthBuffer&&(Z.__webglDepthRenderbuffer=n.createRenderbuffer(),ve(Z.__webglDepthRenderbuffer,P,!0)),t.bindFramebuffer(n.FRAMEBUFFER,null)}}if(Le){t.bindTexture(n.TEXTURE_CUBE_MAP,ae.__webglTexture),ne(n.TEXTURE_CUBE_MAP,x);for(let Se=0;Se<6;Se++)if(x.mipmaps&&x.mipmaps.length>0)for(let we=0;we<x.mipmaps.length;we++)oe(Z.__webglFramebuffer[Se][we],P,x,n.COLOR_ATTACHMENT0,n.TEXTURE_CUBE_MAP_POSITIVE_X+Se,we);else oe(Z.__webglFramebuffer[Se],P,x,n.COLOR_ATTACHMENT0,n.TEXTURE_CUBE_MAP_POSITIVE_X+Se,0);_(x)&&O(n.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(He){for(let Se=0,we=de.length;Se<we;Se++){const Ge=de[Se],Je=i.get(Ge);let Pe=n.TEXTURE_2D;(P.isWebGL3DRenderTarget||P.isWebGLArrayRenderTarget)&&(Pe=P.isWebGL3DRenderTarget?n.TEXTURE_3D:n.TEXTURE_2D_ARRAY),t.bindTexture(Pe,Je.__webglTexture),ne(Pe,Ge),oe(Z.__webglFramebuffer,P,Ge,n.COLOR_ATTACHMENT0+Se,Pe,0),_(Ge)&&O(Pe)}t.unbindTexture()}else{let Se=n.TEXTURE_2D;if((P.isWebGL3DRenderTarget||P.isWebGLArrayRenderTarget)&&(Se=P.isWebGL3DRenderTarget?n.TEXTURE_3D:n.TEXTURE_2D_ARRAY),t.bindTexture(Se,ae.__webglTexture),ne(Se,x),x.mipmaps&&x.mipmaps.length>0)for(let we=0;we<x.mipmaps.length;we++)oe(Z.__webglFramebuffer[we],P,x,n.COLOR_ATTACHMENT0,Se,we);else oe(Z.__webglFramebuffer,P,x,n.COLOR_ATTACHMENT0,Se,0);_(x)&&O(Se),t.unbindTexture()}P.depthBuffer&&Ie(P)}function xe(P){const x=P.textures;for(let Z=0,ae=x.length;Z<ae;Z++){const de=x[Z];if(_(de)){const Le=D(P),He=i.get(de).__webglTexture;t.bindTexture(Le,He),O(Le),t.unbindTexture()}}}const Ee=[],_e=[];function De(P){if(P.samples>0){if(Oe(P)===!1){const x=P.textures,Z=P.width,ae=P.height;let de=n.COLOR_BUFFER_BIT;const Le=P.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,He=i.get(P),Se=x.length>1;if(Se)for(let Ge=0;Ge<x.length;Ge++)t.bindFramebuffer(n.FRAMEBUFFER,He.__webglMultisampledFramebuffer),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+Ge,n.RENDERBUFFER,null),t.bindFramebuffer(n.FRAMEBUFFER,He.__webglFramebuffer),n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0+Ge,n.TEXTURE_2D,null,0);t.bindFramebuffer(n.READ_FRAMEBUFFER,He.__webglMultisampledFramebuffer);const we=P.texture.mipmaps;we&&we.length>0?t.bindFramebuffer(n.DRAW_FRAMEBUFFER,He.__webglFramebuffer[0]):t.bindFramebuffer(n.DRAW_FRAMEBUFFER,He.__webglFramebuffer);for(let Ge=0;Ge<x.length;Ge++){if(P.resolveDepthBuffer&&(P.depthBuffer&&(de|=n.DEPTH_BUFFER_BIT),P.stencilBuffer&&P.resolveStencilBuffer&&(de|=n.STENCIL_BUFFER_BIT)),Se){n.framebufferRenderbuffer(n.READ_FRAMEBUFFER,n.COLOR_ATTACHMENT0,n.RENDERBUFFER,He.__webglColorRenderbuffer[Ge]);const Je=i.get(x[Ge]).__webglTexture;n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0,n.TEXTURE_2D,Je,0)}n.blitFramebuffer(0,0,Z,ae,0,0,Z,ae,de,n.NEAREST),c===!0&&(Ee.length=0,_e.length=0,Ee.push(n.COLOR_ATTACHMENT0+Ge),P.depthBuffer&&P.resolveDepthBuffer===!1&&(Ee.push(Le),_e.push(Le),n.invalidateFramebuffer(n.DRAW_FRAMEBUFFER,_e)),n.invalidateFramebuffer(n.READ_FRAMEBUFFER,Ee))}if(t.bindFramebuffer(n.READ_FRAMEBUFFER,null),t.bindFramebuffer(n.DRAW_FRAMEBUFFER,null),Se)for(let Ge=0;Ge<x.length;Ge++){t.bindFramebuffer(n.FRAMEBUFFER,He.__webglMultisampledFramebuffer),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+Ge,n.RENDERBUFFER,He.__webglColorRenderbuffer[Ge]);const Je=i.get(x[Ge]).__webglTexture;t.bindFramebuffer(n.FRAMEBUFFER,He.__webglFramebuffer),n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0+Ge,n.TEXTURE_2D,Je,0)}t.bindFramebuffer(n.DRAW_FRAMEBUFFER,He.__webglMultisampledFramebuffer)}else if(P.depthBuffer&&P.resolveDepthBuffer===!1&&c){const x=P.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT;n.invalidateFramebuffer(n.DRAW_FRAMEBUFFER,[x])}}}function Ne(P){return Math.min(r.maxSamples,P.samples)}function Oe(P){const x=i.get(P);return P.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&x.__useRenderToTexture!==!1}function J(P){const x=o.render.frame;f.get(P)!==x&&(f.set(P,x),P.update())}function We(P,x){const Z=P.colorSpace,ae=P.format,de=P.type;return P.isCompressedTexture===!0||P.isVideoTexture===!0||Z!==oo&&Z!==Ji&&(bt.getTransfer(Z)===Nt?(ae!==Xn||de!==In)&&ut("WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):Rt("WebGLTextures: Unsupported texture color space:",Z)),x}function Fe(P){return typeof HTMLImageElement<"u"&&P instanceof HTMLImageElement?(u.width=P.naturalWidth||P.width,u.height=P.naturalHeight||P.height):typeof VideoFrame<"u"&&P instanceof VideoFrame?(u.width=P.displayWidth,u.height=P.displayHeight):(u.width=P.width,u.height=P.height),u}this.allocateTextureUnit=T,this.resetTextureUnits=q,this.getTextureUnits=Q,this.setTextureUnits=G,this.setTexture2D=I,this.setTexture2DArray=F,this.setTexture3D=Y,this.setTextureCube=te,this.rebindTextures=be,this.setupRenderTarget=ke,this.updateRenderTargetMipmap=xe,this.updateMultisampleRenderTarget=De,this.setupDepthRenderbuffer=Ie,this.setupFrameBufferTexture=oe,this.useMultisampledRTT=Oe,this.isReversedDepthBuffer=function(){return t.buffers.depth.getReversed()}}function nR(n,e){function t(i,r=Ji){let a;const o=bt.getTransfer(r);if(i===In)return n.UNSIGNED_BYTE;if(i===mu)return n.UNSIGNED_SHORT_4_4_4_4;if(i===gu)return n.UNSIGNED_SHORT_5_5_5_1;if(i===yp)return n.UNSIGNED_INT_5_9_9_9_REV;if(i===Ep)return n.UNSIGNED_INT_10F_11F_11F_REV;if(i===bp)return n.BYTE;if(i===Sp)return n.SHORT;if(i===Za)return n.UNSIGNED_SHORT;if(i===pu)return n.INT;if(i===mi)return n.UNSIGNED_INT;if(i===ci)return n.FLOAT;if(i===ki)return n.HALF_FLOAT;if(i===Mp)return n.ALPHA;if(i===Tp)return n.RGB;if(i===Xn)return n.RGBA;if(i===Ui)return n.DEPTH_COMPONENT;if(i===mr)return n.DEPTH_STENCIL;if(i===wp)return n.RED;if(i===_u)return n.RED_INTEGER;if(i===Sr)return n.RG;if(i===vu)return n.RG_INTEGER;if(i===xu)return n.RGBA_INTEGER;if(i===Ws||i===$s||i===Xs||i===qs)if(o===Nt)if(a=e.get("WEBGL_compressed_texture_s3tc_srgb"),a!==null){if(i===Ws)return a.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(i===$s)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(i===Xs)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(i===qs)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(a=e.get("WEBGL_compressed_texture_s3tc"),a!==null){if(i===Ws)return a.COMPRESSED_RGB_S3TC_DXT1_EXT;if(i===$s)return a.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(i===Xs)return a.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(i===qs)return a.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(i===Vl||i===Wl||i===$l||i===Xl)if(a=e.get("WEBGL_compressed_texture_pvrtc"),a!==null){if(i===Vl)return a.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(i===Wl)return a.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(i===$l)return a.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(i===Xl)return a.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(i===ql||i===Yl||i===Kl||i===Zl||i===Jl||i===ao||i===Ql)if(a=e.get("WEBGL_compressed_texture_etc"),a!==null){if(i===ql||i===Yl)return o===Nt?a.COMPRESSED_SRGB8_ETC2:a.COMPRESSED_RGB8_ETC2;if(i===Kl)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:a.COMPRESSED_RGBA8_ETC2_EAC;if(i===Zl)return a.COMPRESSED_R11_EAC;if(i===Jl)return a.COMPRESSED_SIGNED_R11_EAC;if(i===ao)return a.COMPRESSED_RG11_EAC;if(i===Ql)return a.COMPRESSED_SIGNED_RG11_EAC}else return null;if(i===jl||i===ec||i===tc||i===nc||i===ic||i===rc||i===ac||i===sc||i===oc||i===lc||i===cc||i===uc||i===dc||i===fc)if(a=e.get("WEBGL_compressed_texture_astc"),a!==null){if(i===jl)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:a.COMPRESSED_RGBA_ASTC_4x4_KHR;if(i===ec)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:a.COMPRESSED_RGBA_ASTC_5x4_KHR;if(i===tc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:a.COMPRESSED_RGBA_ASTC_5x5_KHR;if(i===nc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:a.COMPRESSED_RGBA_ASTC_6x5_KHR;if(i===ic)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:a.COMPRESSED_RGBA_ASTC_6x6_KHR;if(i===rc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:a.COMPRESSED_RGBA_ASTC_8x5_KHR;if(i===ac)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:a.COMPRESSED_RGBA_ASTC_8x6_KHR;if(i===sc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:a.COMPRESSED_RGBA_ASTC_8x8_KHR;if(i===oc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:a.COMPRESSED_RGBA_ASTC_10x5_KHR;if(i===lc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:a.COMPRESSED_RGBA_ASTC_10x6_KHR;if(i===cc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:a.COMPRESSED_RGBA_ASTC_10x8_KHR;if(i===uc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:a.COMPRESSED_RGBA_ASTC_10x10_KHR;if(i===dc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:a.COMPRESSED_RGBA_ASTC_12x10_KHR;if(i===fc)return o===Nt?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:a.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(i===hc||i===pc||i===mc)if(a=e.get("EXT_texture_compression_bptc"),a!==null){if(i===hc)return o===Nt?a.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:a.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(i===pc)return a.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(i===mc)return a.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(i===gc||i===_c||i===so||i===vc)if(a=e.get("EXT_texture_compression_rgtc"),a!==null){if(i===gc)return a.COMPRESSED_RED_RGTC1_EXT;if(i===_c)return a.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(i===so)return a.COMPRESSED_RED_GREEN_RGTC2_EXT;if(i===vc)return a.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return i===Ja?n.UNSIGNED_INT_24_8:n[i]!==void 0?n[i]:null}return{convert:t}}const iR=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,rR=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class aR{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t){if(this.texture===null){const i=new kp(e.texture);(e.depthNear!==t.depthNear||e.depthFar!==t.depthFar)&&(this.depthNear=e.depthNear,this.depthFar=e.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,i=new Kn({vertexShader:iR,fragmentShader:rR,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new gi(new yo(20,20),i)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class sR extends Ar{constructor(e,t){super();const i=this;let r=null,a=1,o=null,l="local-floor",c=1,u=null,f=null,h=null,d=null,p=null,m=null;const E=typeof XRWebGLBinding<"u",g=new aR,_={},O=t.getContextAttributes();let D=null,y=null;const B=[],R=[],C=new xt;let b=null;const A=new Cn;A.viewport=new Gt;const k=new Cn;k.viewport=new Gt;const z=[A,k],H=new gM;let q=null,Q=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(N){let V=B[N];return V===void 0&&(V=new Zo,B[N]=V),V.getTargetRaySpace()},this.getControllerGrip=function(N){let V=B[N];return V===void 0&&(V=new Zo,B[N]=V),V.getGripSpace()},this.getHand=function(N){let V=B[N];return V===void 0&&(V=new Zo,B[N]=V),V.getHandSpace()};function G(N){const V=R.indexOf(N.inputSource);if(V===-1)return;const re=B[V];re!==void 0&&(re.update(N.inputSource,N.frame,u||o),re.dispatchEvent({type:N.type,data:N.inputSource}))}function T(){r.removeEventListener("select",G),r.removeEventListener("selectstart",G),r.removeEventListener("selectend",G),r.removeEventListener("squeeze",G),r.removeEventListener("squeezestart",G),r.removeEventListener("squeezeend",G),r.removeEventListener("end",T),r.removeEventListener("inputsourceschange",w);for(let N=0;N<B.length;N++){const V=R[N];V!==null&&(R[N]=null,B[N].disconnect(V))}q=null,Q=null,g.reset();for(const N in _)delete _[N];e.setRenderTarget(D),p=null,d=null,h=null,r=null,y=null,ne.stop(),i.isPresenting=!1,e.setPixelRatio(b),e.setSize(C.width,C.height,!1),i.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(N){a=N,i.isPresenting===!0&&ut("WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(N){l=N,i.isPresenting===!0&&ut("WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return u||o},this.setReferenceSpace=function(N){u=N},this.getBaseLayer=function(){return d!==null?d:p},this.getBinding=function(){return h===null&&E&&(h=new XRWebGLBinding(r,t)),h},this.getFrame=function(){return m},this.getSession=function(){return r},this.setSession=async function(N){if(r=N,r!==null){if(D=e.getRenderTarget(),r.addEventListener("select",G),r.addEventListener("selectstart",G),r.addEventListener("selectend",G),r.addEventListener("squeeze",G),r.addEventListener("squeezestart",G),r.addEventListener("squeezeend",G),r.addEventListener("end",T),r.addEventListener("inputsourceschange",w),O.xrCompatible!==!0&&await t.makeXRCompatible(),b=e.getPixelRatio(),e.getSize(C),E&&"createProjectionLayer"in XRWebGLBinding.prototype){let re=null,Me=null,fe=null;O.depth&&(fe=O.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,re=O.stencil?mr:Ui,Me=O.stencil?Ja:mi);const oe={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:a};h=this.getBinding(),d=h.createProjectionLayer(oe),r.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),y=new fi(d.textureWidth,d.textureHeight,{format:Xn,type:In,depthTexture:new la(d.textureWidth,d.textureHeight,Me,void 0,void 0,void 0,void 0,void 0,void 0,re),stencilBuffer:O.stencil,colorSpace:e.outputColorSpace,samples:O.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1,resolveStencilBuffer:d.ignoreDepthValues===!1})}else{const re={antialias:O.antialias,alpha:!0,depth:O.depth,stencil:O.stencil,framebufferScaleFactor:a};p=new XRWebGLLayer(r,t,re),r.updateRenderState({baseLayer:p}),e.setPixelRatio(1),e.setSize(p.framebufferWidth,p.framebufferHeight,!1),y=new fi(p.framebufferWidth,p.framebufferHeight,{format:Xn,type:In,colorSpace:e.outputColorSpace,stencilBuffer:O.stencil,resolveDepthBuffer:p.ignoreDepthValues===!1,resolveStencilBuffer:p.ignoreDepthValues===!1})}y.isXRRenderTarget=!0,this.setFoveation(c),u=null,o=await r.requestReferenceSpace(l),ne.setContext(r),ne.start(),i.isPresenting=!0,i.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return g.getDepthTexture()};function w(N){for(let V=0;V<N.removed.length;V++){const re=N.removed[V],Me=R.indexOf(re);Me>=0&&(R[Me]=null,B[Me].disconnect(re))}for(let V=0;V<N.added.length;V++){const re=N.added[V];let Me=R.indexOf(re);if(Me===-1){for(let oe=0;oe<B.length;oe++)if(oe>=R.length){R.push(re),Me=oe;break}else if(R[oe]===null){R[oe]=re,Me=oe;break}if(Me===-1)break}const fe=B[Me];fe&&fe.connect(re)}}const I=new ge,F=new ge;function Y(N,V,re){I.setFromMatrixPosition(V.matrixWorld),F.setFromMatrixPosition(re.matrixWorld);const Me=I.distanceTo(F),fe=V.projectionMatrix.elements,oe=re.projectionMatrix.elements,ve=fe[14]/(fe[10]-1),ye=fe[14]/(fe[10]+1),Ie=(fe[9]+1)/fe[5],be=(fe[9]-1)/fe[5],ke=(fe[8]-1)/fe[0],xe=(oe[8]+1)/oe[0],Ee=ve*ke,_e=ve*xe,De=Me/(-ke+xe),Ne=De*-ke;if(V.matrixWorld.decompose(N.position,N.quaternion,N.scale),N.translateX(Ne),N.translateZ(De),N.matrixWorld.compose(N.position,N.quaternion,N.scale),N.matrixWorldInverse.copy(N.matrixWorld).invert(),fe[10]===-1)N.projectionMatrix.copy(V.projectionMatrix),N.projectionMatrixInverse.copy(V.projectionMatrixInverse);else{const Oe=ve+De,J=ye+De,We=Ee-Ne,Fe=_e+(Me-Ne),P=Ie*ye/J*Oe,x=be*ye/J*Oe;N.projectionMatrix.makePerspective(We,Fe,P,x,Oe,J),N.projectionMatrixInverse.copy(N.projectionMatrix).invert()}}function te(N,V){V===null?N.matrixWorld.copy(N.matrix):N.matrixWorld.multiplyMatrices(V.matrixWorld,N.matrix),N.matrixWorldInverse.copy(N.matrixWorld).invert()}this.updateCamera=function(N){if(r===null)return;let V=N.near,re=N.far;g.texture!==null&&(g.depthNear>0&&(V=g.depthNear),g.depthFar>0&&(re=g.depthFar)),H.near=k.near=A.near=V,H.far=k.far=A.far=re,(q!==H.near||Q!==H.far)&&(r.updateRenderState({depthNear:H.near,depthFar:H.far}),q=H.near,Q=H.far),H.layers.mask=N.layers.mask|6,A.layers.mask=H.layers.mask&-5,k.layers.mask=H.layers.mask&-3;const Me=N.parent,fe=H.cameras;te(H,Me);for(let oe=0;oe<fe.length;oe++)te(fe[oe],Me);fe.length===2?Y(H,A,k):H.projectionMatrix.copy(A.projectionMatrix),X(N,H,Me)};function X(N,V,re){re===null?N.matrix.copy(V.matrixWorld):(N.matrix.copy(re.matrixWorld),N.matrix.invert(),N.matrix.multiply(V.matrixWorld)),N.matrix.decompose(N.position,N.quaternion,N.scale),N.updateMatrixWorld(!0),N.projectionMatrix.copy(V.projectionMatrix),N.projectionMatrixInverse.copy(V.projectionMatrixInverse),N.isPerspectiveCamera&&(N.fov=xc*2*Math.atan(1/N.projectionMatrix.elements[5]),N.zoom=1)}this.getCamera=function(){return H},this.getFoveation=function(){if(!(d===null&&p===null))return c},this.setFoveation=function(N){c=N,d!==null&&(d.fixedFoveation=N),p!==null&&p.fixedFoveation!==void 0&&(p.fixedFoveation=N)},this.hasDepthSensing=function(){return g.texture!==null},this.getDepthSensingMesh=function(){return g.getMesh(H)},this.getCameraTexture=function(N){return _[N]};let K=null;function se(N,V){if(f=V.getViewerPose(u||o),m=V,f!==null){const re=f.views;p!==null&&(e.setRenderTargetFramebuffer(y,p.framebuffer),e.setRenderTarget(y));let Me=!1;re.length!==H.cameras.length&&(H.cameras.length=0,Me=!0);for(let ye=0;ye<re.length;ye++){const Ie=re[ye];let be=null;if(p!==null)be=p.getViewport(Ie);else{const xe=h.getViewSubImage(d,Ie);be=xe.viewport,ye===0&&(e.setRenderTargetTextures(y,xe.colorTexture,xe.depthStencilTexture),e.setRenderTarget(y))}let ke=z[ye];ke===void 0&&(ke=new Cn,ke.layers.enable(ye),ke.viewport=new Gt,z[ye]=ke),ke.matrix.fromArray(Ie.transform.matrix),ke.matrix.decompose(ke.position,ke.quaternion,ke.scale),ke.projectionMatrix.fromArray(Ie.projectionMatrix),ke.projectionMatrixInverse.copy(ke.projectionMatrix).invert(),ke.viewport.set(be.x,be.y,be.width,be.height),ye===0&&(H.matrix.copy(ke.matrix),H.matrix.decompose(H.position,H.quaternion,H.scale)),Me===!0&&H.cameras.push(ke)}const fe=r.enabledFeatures;if(fe&&fe.includes("depth-sensing")&&r.depthUsage=="gpu-optimized"&&E){h=i.getBinding();const ye=h.getDepthInformation(re[0]);ye&&ye.isValid&&ye.texture&&g.init(ye,r.renderState)}if(fe&&fe.includes("camera-access")&&E){e.state.unbindTexture(),h=i.getBinding();for(let ye=0;ye<re.length;ye++){const Ie=re[ye].camera;if(Ie){let be=_[Ie];be||(be=new kp,_[Ie]=be);const ke=h.getCameraImage(Ie);be.sourceTexture=ke}}}}for(let re=0;re<B.length;re++){const Me=R[re],fe=B[re];Me!==null&&fe!==void 0&&fe.update(Me,V,u||o)}K&&K(N,V),V.detectedPlanes&&i.dispatchEvent({type:"planesdetected",data:V}),m=null}const ne=new zp;ne.setAnimationLoop(se),this.setAnimationLoop=function(N){K=N},this.dispose=function(){}}}const oR=new Xt,qp=new ht;qp.set(-1,0,0,0,1,0,0,0,1);function lR(n,e){function t(g,_){g.matrixAutoUpdate===!0&&g.updateMatrix(),_.value.copy(g.matrix)}function i(g,_){_.color.getRGB(g.fogColor.value,Up(n)),_.isFog?(g.fogNear.value=_.near,g.fogFar.value=_.far):_.isFogExp2&&(g.fogDensity.value=_.density)}function r(g,_,O,D,y){_.isNodeMaterial?_.uniformsNeedUpdate=!1:_.isMeshBasicMaterial?a(g,_):_.isMeshLambertMaterial?(a(g,_),_.envMap&&(g.envMapIntensity.value=_.envMapIntensity)):_.isMeshToonMaterial?(a(g,_),h(g,_)):_.isMeshPhongMaterial?(a(g,_),f(g,_),_.envMap&&(g.envMapIntensity.value=_.envMapIntensity)):_.isMeshStandardMaterial?(a(g,_),d(g,_),_.isMeshPhysicalMaterial&&p(g,_,y)):_.isMeshMatcapMaterial?(a(g,_),m(g,_)):_.isMeshDepthMaterial?a(g,_):_.isMeshDistanceMaterial?(a(g,_),E(g,_)):_.isMeshNormalMaterial?a(g,_):_.isLineBasicMaterial?(o(g,_),_.isLineDashedMaterial&&l(g,_)):_.isPointsMaterial?c(g,_,O,D):_.isSpriteMaterial?u(g,_):_.isShadowMaterial?(g.color.value.copy(_.color),g.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function a(g,_){g.opacity.value=_.opacity,_.color&&g.diffuse.value.copy(_.color),_.emissive&&g.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(g.map.value=_.map,t(_.map,g.mapTransform)),_.alphaMap&&(g.alphaMap.value=_.alphaMap,t(_.alphaMap,g.alphaMapTransform)),_.bumpMap&&(g.bumpMap.value=_.bumpMap,t(_.bumpMap,g.bumpMapTransform),g.bumpScale.value=_.bumpScale,_.side===yn&&(g.bumpScale.value*=-1)),_.normalMap&&(g.normalMap.value=_.normalMap,t(_.normalMap,g.normalMapTransform),g.normalScale.value.copy(_.normalScale),_.side===yn&&g.normalScale.value.negate()),_.displacementMap&&(g.displacementMap.value=_.displacementMap,t(_.displacementMap,g.displacementMapTransform),g.displacementScale.value=_.displacementScale,g.displacementBias.value=_.displacementBias),_.emissiveMap&&(g.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,g.emissiveMapTransform)),_.specularMap&&(g.specularMap.value=_.specularMap,t(_.specularMap,g.specularMapTransform)),_.alphaTest>0&&(g.alphaTest.value=_.alphaTest);const O=e.get(_),D=O.envMap,y=O.envMapRotation;D&&(g.envMap.value=D,g.envMapRotation.value.setFromMatrix4(oR.makeRotationFromEuler(y)).transpose(),D.isCubeTexture&&D.isRenderTargetTexture===!1&&g.envMapRotation.value.premultiply(qp),g.reflectivity.value=_.reflectivity,g.ior.value=_.ior,g.refractionRatio.value=_.refractionRatio),_.lightMap&&(g.lightMap.value=_.lightMap,g.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,g.lightMapTransform)),_.aoMap&&(g.aoMap.value=_.aoMap,g.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,g.aoMapTransform))}function o(g,_){g.diffuse.value.copy(_.color),g.opacity.value=_.opacity,_.map&&(g.map.value=_.map,t(_.map,g.mapTransform))}function l(g,_){g.dashSize.value=_.dashSize,g.totalSize.value=_.dashSize+_.gapSize,g.scale.value=_.scale}function c(g,_,O,D){g.diffuse.value.copy(_.color),g.opacity.value=_.opacity,g.size.value=_.size*O,g.scale.value=D*.5,_.map&&(g.map.value=_.map,t(_.map,g.uvTransform)),_.alphaMap&&(g.alphaMap.value=_.alphaMap,t(_.alphaMap,g.alphaMapTransform)),_.alphaTest>0&&(g.alphaTest.value=_.alphaTest)}function u(g,_){g.diffuse.value.copy(_.color),g.opacity.value=_.opacity,g.rotation.value=_.rotation,_.map&&(g.map.value=_.map,t(_.map,g.mapTransform)),_.alphaMap&&(g.alphaMap.value=_.alphaMap,t(_.alphaMap,g.alphaMapTransform)),_.alphaTest>0&&(g.alphaTest.value=_.alphaTest)}function f(g,_){g.specular.value.copy(_.specular),g.shininess.value=Math.max(_.shininess,1e-4)}function h(g,_){_.gradientMap&&(g.gradientMap.value=_.gradientMap)}function d(g,_){g.metalness.value=_.metalness,_.metalnessMap&&(g.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,g.metalnessMapTransform)),g.roughness.value=_.roughness,_.roughnessMap&&(g.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,g.roughnessMapTransform)),_.envMap&&(g.envMapIntensity.value=_.envMapIntensity)}function p(g,_,O){g.ior.value=_.ior,_.sheen>0&&(g.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),g.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(g.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,g.sheenColorMapTransform)),_.sheenRoughnessMap&&(g.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,g.sheenRoughnessMapTransform))),_.clearcoat>0&&(g.clearcoat.value=_.clearcoat,g.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(g.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,g.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(g.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,g.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(g.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,g.clearcoatNormalMapTransform),g.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===yn&&g.clearcoatNormalScale.value.negate())),_.dispersion>0&&(g.dispersion.value=_.dispersion),_.iridescence>0&&(g.iridescence.value=_.iridescence,g.iridescenceIOR.value=_.iridescenceIOR,g.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],g.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(g.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,g.iridescenceMapTransform)),_.iridescenceThicknessMap&&(g.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,g.iridescenceThicknessMapTransform))),_.transmission>0&&(g.transmission.value=_.transmission,g.transmissionSamplerMap.value=O.texture,g.transmissionSamplerSize.value.set(O.width,O.height),_.transmissionMap&&(g.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,g.transmissionMapTransform)),g.thickness.value=_.thickness,_.thicknessMap&&(g.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,g.thicknessMapTransform)),g.attenuationDistance.value=_.attenuationDistance,g.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(g.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(g.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,g.anisotropyMapTransform))),g.specularIntensity.value=_.specularIntensity,g.specularColor.value.copy(_.specularColor),_.specularColorMap&&(g.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,g.specularColorMapTransform)),_.specularIntensityMap&&(g.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,g.specularIntensityMapTransform))}function m(g,_){_.matcap&&(g.matcap.value=_.matcap)}function E(g,_){const O=e.get(_).light;g.referencePosition.value.setFromMatrixPosition(O.matrixWorld),g.nearDistance.value=O.shadow.camera.near,g.farDistance.value=O.shadow.camera.far}return{refreshFogUniforms:i,refreshMaterialUniforms:r}}function cR(n,e,t,i){let r={},a={},o=[];const l=n.getParameter(n.MAX_UNIFORM_BUFFER_BINDINGS);function c(y,B){const R=B.program;i.uniformBlockBinding(y,R)}function u(y,B){let R=r[y.id];R===void 0&&(g(y),R=f(y),r[y.id]=R,y.addEventListener("dispose",O));const C=B.program;i.updateUBOMapping(y,C);const b=e.render.frame;a[y.id]!==b&&(d(y),a[y.id]=b)}function f(y){const B=h();y.__bindingPointIndex=B;const R=n.createBuffer(),C=y.__size,b=y.usage;return n.bindBuffer(n.UNIFORM_BUFFER,R),n.bufferData(n.UNIFORM_BUFFER,C,b),n.bindBuffer(n.UNIFORM_BUFFER,null),n.bindBufferBase(n.UNIFORM_BUFFER,B,R),R}function h(){for(let y=0;y<l;y++)if(o.indexOf(y)===-1)return o.push(y),y;return Rt("WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(y){const B=r[y.id],R=y.uniforms,C=y.__cache;n.bindBuffer(n.UNIFORM_BUFFER,B);for(let b=0,A=R.length;b<A;b++){const k=R[b];if(Array.isArray(k))for(let z=0,H=k.length;z<H;z++)p(k[z],b,z,C);else p(k,b,0,C)}n.bindBuffer(n.UNIFORM_BUFFER,null)}function p(y,B,R,C){if(E(y,B,R,C)===!0){const b=y.__offset,A=y.value;if(Array.isArray(A)){let k=0;for(let z=0;z<A.length;z++){const H=A[z],q=_(H);m(H,y.__data,k),typeof H!="number"&&typeof H!="boolean"&&!H.isMatrix3&&!ArrayBuffer.isView(H)&&(k+=q.storage/Float32Array.BYTES_PER_ELEMENT)}}else m(A,y.__data,0);n.bufferSubData(n.UNIFORM_BUFFER,b,y.__data)}}function m(y,B,R){typeof y=="number"||typeof y=="boolean"?B[0]=y:y.isMatrix3?(B[0]=y.elements[0],B[1]=y.elements[1],B[2]=y.elements[2],B[3]=0,B[4]=y.elements[3],B[5]=y.elements[4],B[6]=y.elements[5],B[7]=0,B[8]=y.elements[6],B[9]=y.elements[7],B[10]=y.elements[8],B[11]=0):ArrayBuffer.isView(y)?B.set(new y.constructor(y.buffer,y.byteOffset,B.length)):y.toArray(B,R)}function E(y,B,R,C){const b=y.value,A=B+"_"+R;if(C[A]===void 0)return typeof b=="number"||typeof b=="boolean"?C[A]=b:ArrayBuffer.isView(b)?C[A]=b.slice():C[A]=b.clone(),!0;{const k=C[A];if(typeof b=="number"||typeof b=="boolean"){if(k!==b)return C[A]=b,!0}else{if(ArrayBuffer.isView(b))return!0;if(k.equals(b)===!1)return k.copy(b),!0}}return!1}function g(y){const B=y.uniforms;let R=0;const C=16;for(let A=0,k=B.length;A<k;A++){const z=Array.isArray(B[A])?B[A]:[B[A]];for(let H=0,q=z.length;H<q;H++){const Q=z[H],G=Array.isArray(Q.value)?Q.value:[Q.value];for(let T=0,w=G.length;T<w;T++){const I=G[T],F=_(I),Y=R%C,te=Y%F.boundary,X=Y+te;R+=te,X!==0&&C-X<F.storage&&(R+=C-X),Q.__data=new Float32Array(F.storage/Float32Array.BYTES_PER_ELEMENT),Q.__offset=R,R+=F.storage}}}const b=R%C;return b>0&&(R+=C-b),y.__size=R,y.__cache={},this}function _(y){const B={boundary:0,storage:0};return typeof y=="number"||typeof y=="boolean"?(B.boundary=4,B.storage=4):y.isVector2?(B.boundary=8,B.storage=8):y.isVector3||y.isColor?(B.boundary=16,B.storage=12):y.isVector4?(B.boundary=16,B.storage=16):y.isMatrix3?(B.boundary=48,B.storage=48):y.isMatrix4?(B.boundary=64,B.storage=64):y.isTexture?ut("WebGLRenderer: Texture samplers can not be part of an uniforms group."):ArrayBuffer.isView(y)?(B.boundary=16,B.storage=y.byteLength):ut("WebGLRenderer: Unsupported uniform value type.",y),B}function O(y){const B=y.target;B.removeEventListener("dispose",O);const R=o.indexOf(B.__bindingPointIndex);o.splice(R,1),n.deleteBuffer(r[B.id]),delete r[B.id],delete a[B.id]}function D(){for(const y in r)n.deleteBuffer(r[y]);o=[],r={},a={}}return{bind:c,update:u,dispose:D}}const uR=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]);let ti=null;function dR(){return ti===null&&(ti=new eM(uR,16,16,Sr,ki),ti.name="DFG_LUT",ti.minFilter=fn,ti.magFilter=fn,ti.wrapS=wi,ti.wrapT=wi,ti.generateMipmaps=!1,ti.needsUpdate=!0),ti}class fR{constructor(e={}){const{canvas:t=IE(),context:i=null,depth:r=!0,stencil:a=!1,alpha:o=!1,antialias:l=!1,premultipliedAlpha:c=!0,preserveDrawingBuffer:u=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:h=!1,reversedDepthBuffer:d=!1,outputBufferType:p=In}=e;this.isWebGLRenderer=!0;let m;if(i!==null){if(typeof WebGLRenderingContext<"u"&&i instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");m=i.getContextAttributes().alpha}else m=o;const E=p,g=new Set([xu,vu,_u]),_=new Set([In,mi,Za,Ja,mu,gu]),O=new Uint32Array(4),D=new Int32Array(4),y=new ge;let B=null,R=null;const C=[],b=[];let A=null;this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=di,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const k=this;let z=!1,H=null,q=null,Q=null,G=null;this._outputColorSpace=Rn;let T=0,w=0,I=null,F=-1,Y=null;const te=new Gt,X=new Gt;let K=null;const se=new Ct(0);let ne=0,N=t.width,V=t.height,re=1,Me=null,fe=null;const oe=new Gt(0,0,N,V),ve=new Gt(0,0,N,V);let ye=!1;const Ie=new Mu;let be=!1,ke=!1;const xe=new Xt,Ee=new ge,_e=new Gt,De={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ne=!1;function Oe(){return I===null?re:1}let J=i;function We(v,$){return t.getContext(v,$)}try{const v={alpha:!0,depth:r,stencil:a,antialias:l,premultipliedAlpha:c,preserveDrawingBuffer:u,powerPreference:f,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${fu}`),t.addEventListener("webglcontextlost",It,!1),t.addEventListener("webglcontextrestored",yt,!1),t.addEventListener("webglcontextcreationerror",Mn,!1),J===null){const $="webgl2";if(J=We($,v),J===null)throw We($)?new Error("THREE.WebGLRenderer: Error creating WebGL context with your selected attributes."):new Error("THREE.WebGLRenderer: Error creating WebGL context.")}}catch(v){throw Rt("WebGLRenderer: "+v.message),v}let Fe,P,x,Z,ae,de,Le,He,Se,we,Ge,Je,Pe,Ce,qe,je,st,ce,Be,Te,Ve,Ye,Ue;function nt(){Fe=new d1(J),Fe.init(),Ve=new nR(J,Fe),P=new i1(J,Fe,e,Ve),x=new eR(J,Fe),P.reversedDepthBuffer&&d&&x.buffers.depth.setReversed(!0),q=J.createFramebuffer(),Q=J.createFramebuffer(),G=J.createFramebuffer(),Z=new p1(J),ae=new zA,de=new tR(J,Fe,x,ae,P,Ve,Z),Le=new u1(k),He=new vM(J),Ye=new t1(J,He),Se=new f1(J,He,Z,Ye),we=new g1(J,Se,He,Ye,Z),ce=new m1(J,P,de),qe=new r1(ae),Ge=new BA(k,Le,Fe,P,Ye,qe),Je=new lR(k,ae),Pe=new GA,Ce=new YA(Fe),st=new e1(k,Le,x,we,m,c),je=new jA(k,we,P),Ue=new cR(J,Z,P,x),Be=new n1(J,Fe,Z),Te=new h1(J,Fe,Z),Z.programs=Ge.programs,k.capabilities=P,k.extensions=Fe,k.properties=ae,k.renderLists=Pe,k.shadowMap=je,k.state=x,k.info=Z}nt(),E!==In&&(A=new v1(E,t.width,t.height,l,r,a));const $e=new sR(k,J);this.xr=$e,this.getContext=function(){return J},this.getContextAttributes=function(){return J.getContextAttributes()},this.forceContextLoss=function(){const v=Fe.get("WEBGL_lose_context");v&&v.loseContext()},this.forceContextRestore=function(){const v=Fe.get("WEBGL_lose_context");v&&v.restoreContext()},this.getPixelRatio=function(){return re},this.setPixelRatio=function(v){v!==void 0&&(re=v,this.setSize(N,V,!1))},this.getSize=function(v){return v.set(N,V)},this.setSize=function(v,$,le=!0){if($e.isPresenting){ut("WebGLRenderer: Can't change size while VR device is presenting.");return}N=v,V=$,t.width=Math.floor(v*re),t.height=Math.floor($*re),le===!0&&(t.style.width=v+"px",t.style.height=$+"px"),A!==null&&A.setSize(t.width,t.height),this.setViewport(0,0,v,$)},this.getDrawingBufferSize=function(v){return v.set(N*re,V*re).floor()},this.setDrawingBufferSize=function(v,$,le){N=v,V=$,re=le,t.width=Math.floor(v*le),t.height=Math.floor($*le),this.setViewport(0,0,v,$)},this.setEffects=function(v){if(E===In){Rt("WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.");return}if(v){for(let $=0;$<v.length;$++)if(v[$].isOutputPass===!0){ut("WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.");break}}A.setEffects(v||[])},this.getCurrentViewport=function(v){return v.copy(te)},this.getViewport=function(v){return v.copy(oe)},this.setViewport=function(v,$,le,pe){v.isVector4?oe.set(v.x,v.y,v.z,v.w):oe.set(v,$,le,pe),x.viewport(te.copy(oe).multiplyScalar(re).round())},this.getScissor=function(v){return v.copy(ve)},this.setScissor=function(v,$,le,pe){v.isVector4?ve.set(v.x,v.y,v.z,v.w):ve.set(v,$,le,pe),x.scissor(X.copy(ve).multiplyScalar(re).round())},this.getScissorTest=function(){return ye},this.setScissorTest=function(v){x.setScissorTest(ye=v)},this.setOpaqueSort=function(v){Me=v},this.setTransparentSort=function(v){fe=v},this.getClearColor=function(v){return v.copy(st.getClearColor())},this.setClearColor=function(){st.setClearColor(...arguments)},this.getClearAlpha=function(){return st.getClearAlpha()},this.setClearAlpha=function(){st.setClearAlpha(...arguments)},this.clear=function(v=!0,$=!0,le=!0){let pe=0;if(v){let he=!1;if(I!==null){const ze=I.texture.format;he=g.has(ze)}if(he){const ze=I.texture.type,Ke=_.has(ze),Xe=st.getClearColor(),Qe=st.getClearAlpha(),rt=Xe.r,at=Xe.g,pt=Xe.b;Ke?(O[0]=rt,O[1]=at,O[2]=pt,O[3]=Qe,J.clearBufferuiv(J.COLOR,0,O)):(D[0]=rt,D[1]=at,D[2]=pt,D[3]=Qe,J.clearBufferiv(J.COLOR,0,D))}else pe|=J.COLOR_BUFFER_BIT}$&&(pe|=J.DEPTH_BUFFER_BIT,this.state.buffers.depth.setMask(!0)),le&&(pe|=J.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),pe!==0&&J.clear(pe)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.setNodesHandler=function(v){v.setRenderer(this),H=v},this.dispose=function(){t.removeEventListener("webglcontextlost",It,!1),t.removeEventListener("webglcontextrestored",yt,!1),t.removeEventListener("webglcontextcreationerror",Mn,!1),st.dispose(),Pe.dispose(),Ce.dispose(),ae.dispose(),Le.dispose(),we.dispose(),Ye.dispose(),Ue.dispose(),Ge.dispose(),$e.dispose(),$e.removeEventListener("sessionstart",ma),$e.removeEventListener("sessionend",ga),Zn.stop()};function It(v){v.preventDefault(),Xd("WebGLRenderer: Context Lost."),z=!0}function yt(){Xd("WebGLRenderer: Context Restored."),z=!1;const v=Z.autoReset,$=je.enabled,le=je.autoUpdate,pe=je.needsUpdate,he=je.type;nt(),Z.autoReset=v,je.enabled=$,je.autoUpdate=le,je.needsUpdate=pe,je.type=he}function Mn(v){Rt("WebGLRenderer: A WebGL context could not be created. Reason: ",v.statusMessage)}function xn(v){const $=v.target;$.removeEventListener("dispose",xn),ls($)}function ls(v){cs(v),ae.remove(v)}function cs(v){const $=ae.get(v).programs;$!==void 0&&($.forEach(function(le){Ge.releaseProgram(le)}),v.isShaderMaterial&&Ge.releaseShaderCache(v))}this.renderBufferDirect=function(v,$,le,pe,he,ze){$===null&&($=De);const Ke=he.isMesh&&he.matrixWorld.determinantAffine()<0,Xe=Rr(v,$,le,pe,he);x.setMaterial(pe,Ke);let Qe=le.index,rt=1;if(pe.wireframe===!0){if(Qe=Se.getWireframeAttribute(le),Qe===void 0)return;rt=2}const at=le.drawRange,pt=le.attributes.position;let ot=at.start*rt,Lt=(at.start+at.count)*rt;ze!==null&&(ot=Math.max(ot,ze.start*rt),Lt=Math.min(Lt,(ze.start+ze.count)*rt)),Qe!==null?(ot=Math.max(ot,0),Lt=Math.min(Lt,Qe.count)):pt!=null&&(ot=Math.max(ot,0),Lt=Math.min(Lt,pt.count));const qt=Lt-ot;if(qt<0||qt===1/0)return;Ye.setup(he,pe,Xe,le,Qe);let Vt,Ut=Be;if(Qe!==null&&(Vt=He.get(Qe),Ut=Te,Ut.setIndex(Vt)),he.isMesh)pe.wireframe===!0?(x.setLineWidth(pe.wireframeLinewidth*Oe()),Ut.setMode(J.LINES)):Ut.setMode(J.TRIANGLES);else if(he.isLine){let sn=pe.linewidth;sn===void 0&&(sn=1),x.setLineWidth(sn*Oe()),he.isLineSegments?Ut.setMode(J.LINES):he.isLineLoop?Ut.setMode(J.LINE_LOOP):Ut.setMode(J.LINE_STRIP)}else he.isPoints?Ut.setMode(J.POINTS):he.isSprite&&Ut.setMode(J.TRIANGLES);if(he.isBatchedMesh)if(Fe.get("WEBGL_multi_draw"))Ut.renderMultiDraw(he._multiDrawStarts,he._multiDrawCounts,he._multiDrawCount);else{const sn=he._multiDrawStarts,et=he._multiDrawCounts,Tn=he._multiDrawCount,At=Qe?He.get(Qe).bytesPerElement:1,Nn=ae.get(pe).currentProgram.getUniforms();for(let Jn=0;Jn<Tn;Jn++)Nn.setValue(J,"_gl_DrawID",Jn),Ut.render(sn[Jn]/At,et[Jn])}else if(he.isInstancedMesh)Ut.renderInstances(ot,qt,he.count);else if(le.isInstancedBufferGeometry){const sn=le._maxInstanceCount!==void 0?le._maxInstanceCount:1/0,et=Math.min(le.instanceCount,sn);Ut.renderInstances(ot,qt,et)}else Ut.render(ot,qt)};function us(v,$,le){v.transparent===!0&&v.side===oi&&v.forceSinglePass===!1?(v.side=yn,v.needsUpdate=!0,ar(v,$,le),v.side=ir,v.needsUpdate=!0,ar(v,$,le),v.side=oi):ar(v,$,le)}this.compile=function(v,$,le=null){le===null&&(le=v),R=Ce.get(le),R.init($),b.push(R),le.traverseVisible(function(he){he.isLight&&he.layers.test($.layers)&&(R.pushLight(he),he.castShadow&&R.pushShadow(he))}),v!==le&&v.traverseVisible(function(he){he.isLight&&he.layers.test($.layers)&&(R.pushLight(he),he.castShadow&&R.pushShadow(he))}),R.setupLights();const pe=new Set;return v.traverse(function(he){if(!(he.isMesh||he.isPoints||he.isLine||he.isSprite))return;const ze=he.material;if(ze)if(Array.isArray(ze))for(let Ke=0;Ke<ze.length;Ke++){const Xe=ze[Ke];us(Xe,le,he),pe.add(Xe)}else us(ze,le,he),pe.add(ze)}),R=b.pop(),pe},this.compileAsync=function(v,$,le=null){const pe=this.compile(v,$,le);return new Promise(he=>{function ze(){if(pe.forEach(function(Ke){ae.get(Ke).currentProgram.isReady()&&pe.delete(Ke)}),pe.size===0){he(v);return}setTimeout(ze,10)}Fe.get("KHR_parallel_shader_compile")!==null?ze():setTimeout(ze,10)})};let hn=null;function xi(v){hn&&hn(v)}function ma(){Zn.stop()}function ga(){Zn.start()}const Zn=new zp;Zn.setAnimationLoop(xi),typeof self<"u"&&Zn.setContext(self),this.setAnimationLoop=function(v){hn=v,$e.setAnimationLoop(v),v===null?Zn.stop():Zn.start()},$e.addEventListener("sessionstart",ma),$e.addEventListener("sessionend",ga),this.render=function(v,$){if($!==void 0&&$.isCamera!==!0){Rt("WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(z===!0)return;H!==null&&H.renderStart(v,$);const le=$e.enabled===!0&&$e.isPresenting===!0,pe=A!==null&&(I===null||le)&&A.begin(k,I);if(v.matrixWorldAutoUpdate===!0&&v.updateMatrixWorld(),$.parent===null&&$.matrixWorldAutoUpdate===!0&&$.updateMatrixWorld(),$e.enabled===!0&&$e.isPresenting===!0&&(A===null||A.isCompositing()===!1)&&($e.cameraAutoUpdate===!0&&$e.updateCamera($),$=$e.getCamera()),v.isScene===!0&&v.onBeforeRender(k,v,$,I),R=Ce.get(v,b.length),R.init($),R.state.textureUnits=de.getTextureUnits(),b.push(R),xe.multiplyMatrices($.projectionMatrix,$.matrixWorldInverse),Ie.setFromProjectionMatrix(xe,ui,$.reversedDepth),ke=this.localClippingEnabled,be=qe.init(this.clippingPlanes,ke),B=Pe.get(v,C.length),B.init(),C.push(B),$e.enabled===!0&&$e.isPresenting===!0){const Ke=k.xr.getDepthSensingMesh();Ke!==null&&Oi(Ke,$,-1/0,k.sortObjects)}Oi(v,$,0,k.sortObjects),B.finish(),k.sortObjects===!0&&B.sort(Me,fe,$.reversedDepth),Ne=$e.enabled===!1||$e.isPresenting===!1||$e.hasDepthSensing()===!1,Ne&&st.addToRenderList(B,v),this.info.render.frame++,this.info.autoReset===!0&&this.info.reset(),be===!0&&qe.beginShadows();const he=R.state.shadowsArray;if(je.render(he,v,$),be===!0&&qe.endShadows(),(pe&&A.hasRenderPass())===!1){const Ke=B.opaque,Xe=B.transmissive;if(R.setupLights(),$.isArrayCamera){const Qe=$.cameras;if(Xe.length>0)for(let rt=0,at=Qe.length;rt<at;rt++){const pt=Qe[rt];rr(Ke,Xe,v,pt)}Ne&&st.render(v);for(let rt=0,at=Qe.length;rt<at;rt++){const pt=Qe[rt];Fi(B,v,pt,pt.viewport)}}else Xe.length>0&&rr(Ke,Xe,v,$),Ne&&st.render(v),Fi(B,v,$)}I!==null&&w===0&&(de.updateMultisampleRenderTarget(I),de.updateRenderTargetMipmap(I)),pe&&A.end(k),v.isScene===!0&&v.onAfterRender(k,v,$),Ye.resetDefaultState(),F=-1,Y=null,b.pop(),b.length>0?(R=b[b.length-1],de.setTextureUnits(R.state.textureUnits),be===!0&&qe.setGlobalState(k.clippingPlanes,R.state.camera)):R=null,C.pop(),C.length>0?B=C[C.length-1]:B=null,H!==null&&H.renderEnd()};function Oi(v,$,le,pe){if(v.visible===!1)return;if(v.layers.test($.layers)){if(v.isGroup)le=v.renderOrder;else if(v.isLOD)v.autoUpdate===!0&&v.update($);else if(v.isLightProbeGrid)R.pushLightProbeGrid(v);else if(v.isLight)R.pushLight(v),v.castShadow&&R.pushShadow(v);else if(v.isSprite){if(!v.frustumCulled||Ie.intersectsSprite(v)){pe&&_e.setFromMatrixPosition(v.matrixWorld).applyMatrix4(xe);const Ke=we.update(v),Xe=v.material;Xe.visible&&B.push(v,Ke,Xe,le,_e.z,null)}}else if((v.isMesh||v.isLine||v.isPoints)&&(!v.frustumCulled||Ie.intersectsObject(v))){const Ke=we.update(v),Xe=v.material;if(pe&&(v.boundingSphere!==void 0?(v.boundingSphere===null&&v.computeBoundingSphere(),_e.copy(v.boundingSphere.center)):(Ke.boundingSphere===null&&Ke.computeBoundingSphere(),_e.copy(Ke.boundingSphere.center)),_e.applyMatrix4(v.matrixWorld).applyMatrix4(xe)),Array.isArray(Xe)){const Qe=Ke.groups;for(let rt=0,at=Qe.length;rt<at;rt++){const pt=Qe[rt],ot=Xe[pt.materialIndex];ot&&ot.visible&&B.push(v,Ke,ot,le,_e.z,pt)}}else Xe.visible&&B.push(v,Ke,Xe,le,_e.z,null)}}const ze=v.children;for(let Ke=0,Xe=ze.length;Ke<Xe;Ke++)Oi(ze[Ke],$,le,pe)}function Fi(v,$,le,pe){const{opaque:he,transmissive:ze,transparent:Ke}=v;R.setupLightsView(le),be===!0&&qe.setGlobalState(k.clippingPlanes,le),pe&&x.viewport(te.copy(pe)),he.length>0&&bn(he,$,le),ze.length>0&&bn(ze,$,le),Ke.length>0&&bn(Ke,$,le),x.buffers.depth.setTest(!0),x.buffers.depth.setMask(!0),x.buffers.color.setMask(!0),x.setPolygonOffset(!1)}function rr(v,$,le,pe){if((le.isScene===!0?le.overrideMaterial:null)!==null)return;if(R.state.transmissionRenderTarget[pe.id]===void 0){const ot=Fe.has("EXT_color_buffer_half_float")||Fe.has("EXT_color_buffer_float");R.state.transmissionRenderTarget[pe.id]=new fi(1,1,{generateMipmaps:!0,type:ot?ki:In,minFilter:pr,samples:Math.max(4,P.samples),stencilBuffer:a,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:bt.workingColorSpace})}const ze=R.state.transmissionRenderTarget[pe.id],Ke=pe.viewport||te;ze.setSize(Ke.z*k.transmissionResolutionScale,Ke.w*k.transmissionResolutionScale);const Xe=k.getRenderTarget(),Qe=k.getActiveCubeFace(),rt=k.getActiveMipmapLevel();k.setRenderTarget(ze),k.getClearColor(se),ne=k.getClearAlpha(),ne<1&&k.setClearColor(16777215,.5),k.clear(),Ne&&st.render(le);const at=k.toneMapping;k.toneMapping=di;const pt=pe.viewport;if(pe.viewport!==void 0&&(pe.viewport=void 0),R.setupLightsView(pe),be===!0&&qe.setGlobalState(k.clippingPlanes,pe),bn(v,le,pe),de.updateMultisampleRenderTarget(ze),de.updateRenderTargetMipmap(ze),Fe.has("WEBGL_multisampled_render_to_texture")===!1){let ot=!1;for(let Lt=0,qt=$.length;Lt<qt;Lt++){const Vt=$[Lt],{object:Ut,geometry:sn,material:et,group:Tn}=Vt;if(et.side===oi&&Ut.layers.test(pe.layers)){const At=et.side;et.side=yn,et.needsUpdate=!0,_a(Ut,le,pe,sn,et,Tn),et.side=At,et.needsUpdate=!0,ot=!0}}ot===!0&&(de.updateMultisampleRenderTarget(ze),de.updateRenderTargetMipmap(ze))}k.setRenderTarget(Xe,Qe,rt),k.setClearColor(se,ne),pt!==void 0&&(pe.viewport=pt),k.toneMapping=at}function bn(v,$,le){const pe=$.isScene===!0?$.overrideMaterial:null;for(let he=0,ze=v.length;he<ze;he++){const Ke=v[he],{object:Xe,geometry:Qe,group:rt}=Ke;let at=Ke.material;at.allowOverride===!0&&pe!==null&&(at=pe),Xe.layers.test(le.layers)&&_a(Xe,$,le,Qe,at,rt)}}function _a(v,$,le,pe,he,ze){v.onBeforeRender(k,$,le,pe,he,ze),v.modelViewMatrix.multiplyMatrices(le.matrixWorldInverse,v.matrixWorld),v.normalMatrix.getNormalMatrix(v.modelViewMatrix),he.onBeforeRender(k,$,le,pe,v,ze),he.transparent===!0&&he.side===oi&&he.forceSinglePass===!1?(he.side=yn,he.needsUpdate=!0,k.renderBufferDirect(le,$,pe,he,v,ze),he.side=ir,he.needsUpdate=!0,k.renderBufferDirect(le,$,pe,he,v,ze),he.side=oi):k.renderBufferDirect(le,$,pe,he,v,ze),v.onAfterRender(k,$,le,pe,he,ze)}function ar(v,$,le){$.isScene!==!0&&($=De);const pe=ae.get(v),he=R.state.lights,ze=R.state.shadowsArray,Ke=he.state.version,Xe=Ge.getParameters(v,he.state,ze,$,le,R.state.lightProbeGridArray),Qe=Ge.getProgramCacheKey(Xe);let rt=pe.programs;pe.environment=v.isMeshStandardMaterial||v.isMeshLambertMaterial||v.isMeshPhongMaterial?$.environment:null,pe.fog=$.fog;const at=v.isMeshStandardMaterial||v.isMeshLambertMaterial&&!v.envMap||v.isMeshPhongMaterial&&!v.envMap;pe.envMap=Le.get(v.envMap||pe.environment,at),pe.envMapRotation=pe.environment!==null&&v.envMap===null?$.environmentRotation:v.envMapRotation,rt===void 0&&(v.addEventListener("dispose",xn),rt=new Map,pe.programs=rt);let pt=rt.get(Qe);if(pt!==void 0){if(pe.currentProgram===pt&&pe.lightsStateVersion===Ke)return va(v,Xe),pt}else Xe.uniforms=Ge.getUniforms(v),H!==null&&v.isNodeMaterial&&H.build(v,le,Xe),v.onBeforeCompile(Xe,k),pt=Ge.acquireProgram(Xe,Qe),rt.set(Qe,pt),pe.uniforms=Xe.uniforms;const ot=pe.uniforms;return(!v.isShaderMaterial&&!v.isRawShaderMaterial||v.clipping===!0)&&(ot.clippingPlanes=qe.uniform),va(v,Xe),pe.needsLights=it(v),pe.lightsStateVersion=Ke,pe.needsLights&&(ot.ambientLightColor.value=he.state.ambient,ot.lightProbe.value=he.state.probe,ot.directionalLights.value=he.state.directional,ot.directionalLightShadows.value=he.state.directionalShadow,ot.spotLights.value=he.state.spot,ot.spotLightShadows.value=he.state.spotShadow,ot.rectAreaLights.value=he.state.rectArea,ot.ltc_1.value=he.state.rectAreaLTC1,ot.ltc_2.value=he.state.rectAreaLTC2,ot.pointLights.value=he.state.point,ot.pointLightShadows.value=he.state.pointShadow,ot.hemisphereLights.value=he.state.hemi,ot.directionalShadowMatrix.value=he.state.directionalShadowMatrix,ot.spotLightMatrix.value=he.state.spotLightMatrix,ot.spotLightMap.value=he.state.spotLightMap,ot.pointShadowMatrix.value=he.state.pointShadowMatrix),pe.lightProbeGrid=R.state.lightProbeGridArray.length>0,pe.currentProgram=pt,pe.uniformsList=null,pt}function ds(v){if(v.uniformsList===null){const $=v.currentProgram.getUniforms();v.uniformsList=Ys.seqWithValue($.seq,v.uniforms)}return v.uniformsList}function va(v,$){const le=ae.get(v);le.outputColorSpace=$.outputColorSpace,le.batching=$.batching,le.batchingColor=$.batchingColor,le.instancing=$.instancing,le.instancingColor=$.instancingColor,le.instancingMorph=$.instancingMorph,le.skinning=$.skinning,le.morphTargets=$.morphTargets,le.morphNormals=$.morphNormals,le.morphColors=$.morphColors,le.morphTargetsCount=$.morphTargetsCount,le.numClippingPlanes=$.numClippingPlanes,le.numIntersection=$.numClipIntersection,le.vertexAlphas=$.vertexAlphas,le.vertexTangents=$.vertexTangents,le.toneMapping=$.toneMapping}function fs(v,$){if(v.length===0)return null;if(v.length===1)return v[0].texture!==null?v[0]:null;y.setFromMatrixPosition($.matrixWorld);for(let le=0,pe=v.length;le<pe;le++){const he=v[le];if(he.texture!==null&&he.boundingBox.containsPoint(y))return he}return null}function Rr(v,$,le,pe,he){$.isScene!==!0&&($=De),de.resetTextureUnits();const ze=$.fog,Ke=pe.isMeshStandardMaterial||pe.isMeshLambertMaterial||pe.isMeshPhongMaterial?$.environment:null,Xe=I===null?k.outputColorSpace:I.isXRRenderTarget===!0?I.texture.colorSpace:bt.workingColorSpace,Qe=pe.isMeshStandardMaterial||pe.isMeshLambertMaterial&&!pe.envMap||pe.isMeshPhongMaterial&&!pe.envMap,rt=Le.get(pe.envMap||Ke,Qe),at=pe.vertexColors===!0&&!!le.attributes.color&&le.attributes.color.itemSize===4,pt=!!le.attributes.tangent&&(!!pe.normalMap||pe.anisotropy>0),ot=!!le.morphAttributes.position,Lt=!!le.morphAttributes.normal,qt=!!le.morphAttributes.color;let Vt=di;pe.toneMapped&&(I===null||I.isXRRenderTarget===!0)&&(Vt=k.toneMapping);const Ut=le.morphAttributes.position||le.morphAttributes.normal||le.morphAttributes.color,sn=Ut!==void 0?Ut.length:0,et=ae.get(pe),Tn=R.state.lights;if(be===!0&&(ke===!0||v!==Y)){const Bt=v===Y&&pe.id===F;qe.setState(pe,v,Bt)}let At=!1;pe.version===et.__version?(et.needsLights&&et.lightsStateVersion!==Tn.state.version||et.outputColorSpace!==Xe||he.isBatchedMesh&&et.batching===!1||!he.isBatchedMesh&&et.batching===!0||he.isBatchedMesh&&et.batchingColor===!0&&he.colorTexture===null||he.isBatchedMesh&&et.batchingColor===!1&&he.colorTexture!==null||he.isInstancedMesh&&et.instancing===!1||!he.isInstancedMesh&&et.instancing===!0||he.isSkinnedMesh&&et.skinning===!1||!he.isSkinnedMesh&&et.skinning===!0||he.isInstancedMesh&&et.instancingColor===!0&&he.instanceColor===null||he.isInstancedMesh&&et.instancingColor===!1&&he.instanceColor!==null||he.isInstancedMesh&&et.instancingMorph===!0&&he.morphTexture===null||he.isInstancedMesh&&et.instancingMorph===!1&&he.morphTexture!==null||et.envMap!==rt||pe.fog===!0&&et.fog!==ze||et.numClippingPlanes!==void 0&&(et.numClippingPlanes!==qe.numPlanes||et.numIntersection!==qe.numIntersection)||et.vertexAlphas!==at||et.vertexTangents!==pt||et.morphTargets!==ot||et.morphNormals!==Lt||et.morphColors!==qt||et.toneMapping!==Vt||et.morphTargetsCount!==sn||!!et.lightProbeGrid!=R.state.lightProbeGridArray.length>0)&&(At=!0):(At=!0,et.__version=pe.version);let Nn=et.currentProgram;At===!0&&(Nn=ar(pe,$,he),H&&pe.isNodeMaterial&&H.onUpdateProgram(pe,Nn,et));let Jn=!1,zi=!1,Cr=!1;const Ot=Nn.getUniforms(),Yt=et.uniforms;if(x.useProgram(Nn.program)&&(Jn=!0,zi=!0,Cr=!0),pe.id!==F&&(F=pe.id,zi=!0),et.needsLights){const Bt=fs(R.state.lightProbeGridArray,he);et.lightProbeGrid!==Bt&&(et.lightProbeGrid=Bt,zi=!0)}if(Jn||Y!==v){x.buffers.depth.getReversed()&&v.reversedDepth!==!0&&(v._reversedDepth=!0,v.updateProjectionMatrix()),Ot.setValue(J,"projectionMatrix",v.projectionMatrix),Ot.setValue(J,"viewMatrix",v.matrixWorldInverse);const Gi=Ot.map.cameraPosition;Gi!==void 0&&Gi.setValue(J,Ee.setFromMatrixPosition(v.matrixWorld)),P.logarithmicDepthBuffer&&Ot.setValue(J,"logDepthBufFC",2/(Math.log(v.far+1)/Math.LN2)),(pe.isMeshPhongMaterial||pe.isMeshToonMaterial||pe.isMeshLambertMaterial||pe.isMeshBasicMaterial||pe.isMeshStandardMaterial||pe.isShaderMaterial)&&Ot.setValue(J,"isOrthographic",v.isOrthographicCamera===!0),Y!==v&&(Y=v,zi=!0,Cr=!0)}if(et.needsLights&&(Tn.state.directionalShadowMap.length>0&&Ot.setValue(J,"directionalShadowMap",Tn.state.directionalShadowMap,de),Tn.state.spotShadowMap.length>0&&Ot.setValue(J,"spotShadowMap",Tn.state.spotShadowMap,de),Tn.state.pointShadowMap.length>0&&Ot.setValue(J,"pointShadowMap",Tn.state.pointShadowMap,de)),he.isSkinnedMesh){Ot.setOptional(J,he,"bindMatrix"),Ot.setOptional(J,he,"bindMatrixInverse");const Bt=he.skeleton;Bt&&(Bt.boneTexture===null&&Bt.computeBoneTexture(),Ot.setValue(J,"boneTexture",Bt.boneTexture,de))}he.isBatchedMesh&&(Ot.setOptional(J,he,"batchingTexture"),Ot.setValue(J,"batchingTexture",he._matricesTexture,de),Ot.setOptional(J,he,"batchingIdTexture"),Ot.setValue(J,"batchingIdTexture",he._indirectTexture,de),Ot.setOptional(J,he,"batchingColorTexture"),he._colorsTexture!==null&&Ot.setValue(J,"batchingColorTexture",he._colorsTexture,de));const Hi=le.morphAttributes;if((Hi.position!==void 0||Hi.normal!==void 0||Hi.color!==void 0)&&ce.update(he,le,Nn),(zi||et.receiveShadow!==he.receiveShadow)&&(et.receiveShadow=he.receiveShadow,Ot.setValue(J,"receiveShadow",he.receiveShadow)),(pe.isMeshStandardMaterial||pe.isMeshLambertMaterial||pe.isMeshPhongMaterial)&&pe.envMap===null&&$.environment!==null&&(Yt.envMapIntensity.value=$.environmentIntensity),Yt.dfgLUT!==void 0&&(Yt.dfgLUT.value=dR()),zi){if(Ot.setValue(J,"toneMappingExposure",k.toneMappingExposure),et.needsLights&&Bi(Yt,Cr),ze&&pe.fog===!0&&Je.refreshFogUniforms(Yt,ze),Je.refreshMaterialUniforms(Yt,pe,re,V,R.state.transmissionRenderTarget[v.id]),et.needsLights&&et.lightProbeGrid){const Bt=et.lightProbeGrid;Yt.probesSH.value=Bt.texture,Yt.probesMin.value.copy(Bt.boundingBox.min),Yt.probesMax.value.copy(Bt.boundingBox.max),Yt.probesResolution.value.copy(Bt.resolution)}Ys.upload(J,ds(et),Yt,de)}if(pe.isShaderMaterial&&pe.uniformsNeedUpdate===!0&&(Ys.upload(J,ds(et),Yt,de),pe.uniformsNeedUpdate=!1),pe.isSpriteMaterial&&Ot.setValue(J,"center",he.center),Ot.setValue(J,"modelViewMatrix",he.modelViewMatrix),Ot.setValue(J,"normalMatrix",he.normalMatrix),Ot.setValue(J,"modelMatrix",he.matrixWorld),pe.uniformsGroups!==void 0){const Bt=pe.uniformsGroups;for(let Gi=0,Ir=Bt.length;Gi<Ir;Gi++){const Lu=Bt[Gi];Ue.update(Lu,Nn),Ue.bind(Lu,Nn)}}return Nn}function Bi(v,$){v.ambientLightColor.needsUpdate=$,v.lightProbe.needsUpdate=$,v.directionalLights.needsUpdate=$,v.directionalLightShadows.needsUpdate=$,v.pointLights.needsUpdate=$,v.pointLightShadows.needsUpdate=$,v.spotLights.needsUpdate=$,v.spotLightShadows.needsUpdate=$,v.rectAreaLights.needsUpdate=$,v.hemisphereLights.needsUpdate=$}function it(v){return v.isMeshLambertMaterial||v.isMeshToonMaterial||v.isMeshPhongMaterial||v.isMeshStandardMaterial||v.isShadowMaterial||v.isShaderMaterial&&v.lights===!0}this.getActiveCubeFace=function(){return T},this.getActiveMipmapLevel=function(){return w},this.getRenderTarget=function(){return I},this.setRenderTargetTextures=function(v,$,le){const pe=ae.get(v);pe.__autoAllocateDepthBuffer=v.resolveDepthBuffer===!1,pe.__autoAllocateDepthBuffer===!1&&(pe.__useRenderToTexture=!1),ae.get(v.texture).__webglTexture=$,ae.get(v.depthTexture).__webglTexture=pe.__autoAllocateDepthBuffer?void 0:le,pe.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(v,$){const le=ae.get(v);le.__webglFramebuffer=$,le.__useDefaultFramebuffer=$===void 0},this.setRenderTarget=function(v,$=0,le=0){I=v,T=$,w=le;let pe=null,he=!1,ze=!1;if(v){const Xe=ae.get(v);if(Xe.__useDefaultFramebuffer!==void 0){x.bindFramebuffer(J.FRAMEBUFFER,Xe.__webglFramebuffer),te.copy(v.viewport),X.copy(v.scissor),K=v.scissorTest,x.viewport(te),x.scissor(X),x.setScissorTest(K),F=-1;return}else if(Xe.__webglFramebuffer===void 0)de.setupRenderTarget(v);else if(Xe.__hasExternalTextures)de.rebindTextures(v,ae.get(v.texture).__webglTexture,ae.get(v.depthTexture).__webglTexture);else if(v.depthBuffer){const at=v.depthTexture;if(Xe.__boundDepthTexture!==at){if(at!==null&&ae.has(at)&&(v.width!==at.image.width||v.height!==at.image.height))throw new Error("THREE.WebGLRenderer: Attached DepthTexture is initialized to the incorrect size.");de.setupDepthRenderbuffer(v)}}const Qe=v.texture;(Qe.isData3DTexture||Qe.isDataArrayTexture||Qe.isCompressedArrayTexture)&&(ze=!0);const rt=ae.get(v).__webglFramebuffer;v.isWebGLCubeRenderTarget?(Array.isArray(rt[$])?pe=rt[$][le]:pe=rt[$],he=!0):v.samples>0&&de.useMultisampledRTT(v)===!1?pe=ae.get(v).__webglMultisampledFramebuffer:Array.isArray(rt)?pe=rt[le]:pe=rt,te.copy(v.viewport),X.copy(v.scissor),K=v.scissorTest}else te.copy(oe).multiplyScalar(re).floor(),X.copy(ve).multiplyScalar(re).floor(),K=ye;if(le!==0&&(pe=q),x.bindFramebuffer(J.FRAMEBUFFER,pe)&&x.drawBuffers(v,pe),x.viewport(te),x.scissor(X),x.setScissorTest(K),he){const Xe=ae.get(v.texture);J.framebufferTexture2D(J.FRAMEBUFFER,J.COLOR_ATTACHMENT0,J.TEXTURE_CUBE_MAP_POSITIVE_X+$,Xe.__webglTexture,le)}else if(ze){const Xe=$;for(let Qe=0;Qe<v.textures.length;Qe++){const rt=ae.get(v.textures[Qe]);J.framebufferTextureLayer(J.FRAMEBUFFER,J.COLOR_ATTACHMENT0+Qe,rt.__webglTexture,le,Xe)}}else if(v!==null&&le!==0){const Xe=ae.get(v.texture);J.framebufferTexture2D(J.FRAMEBUFFER,J.COLOR_ATTACHMENT0,J.TEXTURE_2D,Xe.__webglTexture,le)}F=-1},this.readRenderTargetPixels=function(v,$,le,pe,he,ze,Ke,Xe=0){if(!(v&&v.isWebGLRenderTarget)){Rt("WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Qe=ae.get(v).__webglFramebuffer;if(v.isWebGLCubeRenderTarget&&Ke!==void 0&&(Qe=Qe[Ke]),Qe){x.bindFramebuffer(J.FRAMEBUFFER,Qe);try{const rt=v.textures[Xe],at=rt.format,pt=rt.type;if(v.textures.length>1&&J.readBuffer(J.COLOR_ATTACHMENT0+Xe),!P.textureFormatReadable(at)){Rt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!P.textureTypeReadable(pt)){Rt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}$>=0&&$<=v.width-pe&&le>=0&&le<=v.height-he&&J.readPixels($,le,pe,he,Ve.convert(at),Ve.convert(pt),ze)}finally{const rt=I!==null?ae.get(I).__webglFramebuffer:null;x.bindFramebuffer(J.FRAMEBUFFER,rt)}}},this.readRenderTargetPixelsAsync=async function(v,$,le,pe,he,ze,Ke,Xe=0){if(!(v&&v.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Qe=ae.get(v).__webglFramebuffer;if(v.isWebGLCubeRenderTarget&&Ke!==void 0&&(Qe=Qe[Ke]),Qe)if($>=0&&$<=v.width-pe&&le>=0&&le<=v.height-he){x.bindFramebuffer(J.FRAMEBUFFER,Qe);const rt=v.textures[Xe],at=rt.format,pt=rt.type;if(v.textures.length>1&&J.readBuffer(J.COLOR_ATTACHMENT0+Xe),!P.textureFormatReadable(at))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!P.textureTypeReadable(pt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const ot=J.createBuffer();J.bindBuffer(J.PIXEL_PACK_BUFFER,ot),J.bufferData(J.PIXEL_PACK_BUFFER,ze.byteLength,J.STREAM_READ),J.readPixels($,le,pe,he,Ve.convert(at),Ve.convert(pt),0);const Lt=I!==null?ae.get(I).__webglFramebuffer:null;x.bindFramebuffer(J.FRAMEBUFFER,Lt);const qt=J.fenceSync(J.SYNC_GPU_COMMANDS_COMPLETE,0);return J.flush(),await NE(J,qt,4),J.bindBuffer(J.PIXEL_PACK_BUFFER,ot),J.getBufferSubData(J.PIXEL_PACK_BUFFER,0,ze),J.deleteBuffer(ot),J.deleteSync(qt),ze}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(v,$=null,le=0){const pe=Math.pow(2,-le),he=Math.floor(v.image.width*pe),ze=Math.floor(v.image.height*pe),Ke=$!==null?$.x:0,Xe=$!==null?$.y:0;de.setTexture2D(v,0),J.copyTexSubImage2D(J.TEXTURE_2D,le,0,0,Ke,Xe,he,ze),x.unbindTexture()},this.copyTextureToTexture=function(v,$,le=null,pe=null,he=0,ze=0){let Ke,Xe,Qe,rt,at,pt,ot,Lt,qt;const Vt=v.isCompressedTexture?v.mipmaps[ze]:v.image;if(le!==null)Ke=le.max.x-le.min.x,Xe=le.max.y-le.min.y,Qe=le.isBox3?le.max.z-le.min.z:1,rt=le.min.x,at=le.min.y,pt=le.isBox3?le.min.z:0;else{const Yt=Math.pow(2,-he);Ke=Math.floor(Vt.width*Yt),Xe=Math.floor(Vt.height*Yt),v.isDataArrayTexture?Qe=Vt.depth:v.isData3DTexture?Qe=Math.floor(Vt.depth*Yt):Qe=1,rt=0,at=0,pt=0}pe!==null?(ot=pe.x,Lt=pe.y,qt=pe.z):(ot=0,Lt=0,qt=0);const Ut=Ve.convert($.format),sn=Ve.convert($.type);let et;$.isData3DTexture?(de.setTexture3D($,0),et=J.TEXTURE_3D):$.isDataArrayTexture||$.isCompressedArrayTexture?(de.setTexture2DArray($,0),et=J.TEXTURE_2D_ARRAY):(de.setTexture2D($,0),et=J.TEXTURE_2D),x.activeTexture(J.TEXTURE0),x.pixelStorei(J.UNPACK_FLIP_Y_WEBGL,$.flipY),x.pixelStorei(J.UNPACK_PREMULTIPLY_ALPHA_WEBGL,$.premultiplyAlpha),x.pixelStorei(J.UNPACK_ALIGNMENT,$.unpackAlignment);const Tn=x.getParameter(J.UNPACK_ROW_LENGTH),At=x.getParameter(J.UNPACK_IMAGE_HEIGHT),Nn=x.getParameter(J.UNPACK_SKIP_PIXELS),Jn=x.getParameter(J.UNPACK_SKIP_ROWS),zi=x.getParameter(J.UNPACK_SKIP_IMAGES);x.pixelStorei(J.UNPACK_ROW_LENGTH,Vt.width),x.pixelStorei(J.UNPACK_IMAGE_HEIGHT,Vt.height),x.pixelStorei(J.UNPACK_SKIP_PIXELS,rt),x.pixelStorei(J.UNPACK_SKIP_ROWS,at),x.pixelStorei(J.UNPACK_SKIP_IMAGES,pt);const Cr=v.isDataArrayTexture||v.isData3DTexture,Ot=$.isDataArrayTexture||$.isData3DTexture;if(v.isDepthTexture){const Yt=ae.get(v),Hi=ae.get($),Bt=ae.get(Yt.__renderTarget),Gi=ae.get(Hi.__renderTarget);x.bindFramebuffer(J.READ_FRAMEBUFFER,Bt.__webglFramebuffer),x.bindFramebuffer(J.DRAW_FRAMEBUFFER,Gi.__webglFramebuffer);for(let Ir=0;Ir<Qe;Ir++)Cr&&(J.framebufferTextureLayer(J.READ_FRAMEBUFFER,J.COLOR_ATTACHMENT0,ae.get(v).__webglTexture,he,pt+Ir),J.framebufferTextureLayer(J.DRAW_FRAMEBUFFER,J.COLOR_ATTACHMENT0,ae.get($).__webglTexture,ze,qt+Ir)),J.blitFramebuffer(rt,at,Ke,Xe,ot,Lt,Ke,Xe,J.DEPTH_BUFFER_BIT,J.NEAREST);x.bindFramebuffer(J.READ_FRAMEBUFFER,null),x.bindFramebuffer(J.DRAW_FRAMEBUFFER,null)}else if(he!==0||v.isRenderTargetTexture||ae.has(v)){const Yt=ae.get(v),Hi=ae.get($);x.bindFramebuffer(J.READ_FRAMEBUFFER,Q),x.bindFramebuffer(J.DRAW_FRAMEBUFFER,G);for(let Bt=0;Bt<Qe;Bt++)Cr?J.framebufferTextureLayer(J.READ_FRAMEBUFFER,J.COLOR_ATTACHMENT0,Yt.__webglTexture,he,pt+Bt):J.framebufferTexture2D(J.READ_FRAMEBUFFER,J.COLOR_ATTACHMENT0,J.TEXTURE_2D,Yt.__webglTexture,he),Ot?J.framebufferTextureLayer(J.DRAW_FRAMEBUFFER,J.COLOR_ATTACHMENT0,Hi.__webglTexture,ze,qt+Bt):J.framebufferTexture2D(J.DRAW_FRAMEBUFFER,J.COLOR_ATTACHMENT0,J.TEXTURE_2D,Hi.__webglTexture,ze),he!==0?J.blitFramebuffer(rt,at,Ke,Xe,ot,Lt,Ke,Xe,J.COLOR_BUFFER_BIT,J.NEAREST):Ot?J.copyTexSubImage3D(et,ze,ot,Lt,qt+Bt,rt,at,Ke,Xe):J.copyTexSubImage2D(et,ze,ot,Lt,rt,at,Ke,Xe);x.bindFramebuffer(J.READ_FRAMEBUFFER,null),x.bindFramebuffer(J.DRAW_FRAMEBUFFER,null)}else Ot?v.isDataTexture||v.isData3DTexture?J.texSubImage3D(et,ze,ot,Lt,qt,Ke,Xe,Qe,Ut,sn,Vt.data):$.isCompressedArrayTexture?J.compressedTexSubImage3D(et,ze,ot,Lt,qt,Ke,Xe,Qe,Ut,Vt.data):J.texSubImage3D(et,ze,ot,Lt,qt,Ke,Xe,Qe,Ut,sn,Vt):v.isDataTexture?J.texSubImage2D(J.TEXTURE_2D,ze,ot,Lt,Ke,Xe,Ut,sn,Vt.data):v.isCompressedTexture?J.compressedTexSubImage2D(J.TEXTURE_2D,ze,ot,Lt,Vt.width,Vt.height,Ut,Vt.data):J.texSubImage2D(J.TEXTURE_2D,ze,ot,Lt,Ke,Xe,Ut,sn,Vt);x.pixelStorei(J.UNPACK_ROW_LENGTH,Tn),x.pixelStorei(J.UNPACK_IMAGE_HEIGHT,At),x.pixelStorei(J.UNPACK_SKIP_PIXELS,Nn),x.pixelStorei(J.UNPACK_SKIP_ROWS,Jn),x.pixelStorei(J.UNPACK_SKIP_IMAGES,zi),ze===0&&$.generateMipmaps&&J.generateMipmap(et),x.unbindTexture()},this.initRenderTarget=function(v){ae.get(v).__webglFramebuffer===void 0&&de.setupRenderTarget(v)},this.initTexture=function(v){v.isCubeTexture?de.setTextureCube(v,0):v.isData3DTexture?de.setTexture3D(v,0):v.isDataArrayTexture||v.isCompressedArrayTexture?de.setTexture2DArray(v,0):de.setTexture2D(v,0),x.unbindTexture()},this.resetState=function(){T=0,w=0,I=null,x.reset(),Ye.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return ui}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=bt._getDrawingBufferColorSpace(e),t.unpackColorSpace=bt._getUnpackColorSpace()}}const hR=`
uniform float uTime;
uniform float uLevel;
uniform int uState;
uniform vec3 cameraPos;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;

float hash(vec3 p) {
  return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

float noise(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(hash(i + vec3(0,0,0)), hash(i + vec3(1,0,0)), f.x),
        mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
    mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
        mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y),
    f.z
  );
}

void main() {
  vec3 pos = position;
  float t = uTime;
  float amp = 0.06 + uLevel * 0.42;
  if (uState == 2) amp += 0.12;
  if (uState == 3) amp += 0.06;
  float n1 = noise(pos * 3.2 + t * 0.55);
  float n2 = noise(pos * 6.1 - t * 0.95);
  float disp = (n1 * 0.65 + n2 * 0.35) * amp;
  pos += normal * disp;

  vec4 worldPos = modelMatrix * vec4(pos, 1.0);
  vWorldPos = worldPos.xyz;
  vWorldNormal = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
`,pR=`
uniform vec3 uColorA;
uniform vec3 uColorB;
uniform float uLevel;
uniform float uTime;
uniform int uState;
uniform vec3 cameraPos;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;

void main() {
  vec3 viewDir = normalize(cameraPos - vWorldPos);
  vec3 n = normalize(vWorldNormal);
  float fresnel = pow(1.0 - clamp(dot(n, viewDir), 0.0, 1.0), 2.2);
  float pulse = uLevel * 0.35;
  if (uState == 2) pulse += 0.08 * sin(uTime * 8.0);
  vec3 col = mix(uColorA, uColorB, fresnel + pulse);
  float alpha = 0.78 + fresnel * 0.2 + uLevel * 0.08;
  gl_FragColor = vec4(col, alpha);
}
`,mR={idle:0,wake_detected:1,listening:1,processing:2,speaking:3};function gR(n){const e=new fR({antialias:!0,alpha:!0});e.setPixelRatio(Math.min(window.devicePixelRatio,2)),e.setSize(n.clientWidth,n.clientHeight),e.setClearColor(0,0),e.outputColorSpace=Rn,e.toneMapping=hu,n.appendChild(e.domElement);const t=new qE,i=new Cn(50,n.clientWidth/Math.max(n.clientHeight,1),.1,100),r=1.7;function a(_,O){const D=_/Math.max(O,1),y=i.fov*Math.PI/180,B=Math.tan(y/2),R=r/B,C=r/(B*D);return Math.max(3.2,R,C)}i.position.set(0,0,3.4),t.add(new pM(3359846,.4));const o=new hf(8965375,1.4,24);o.position.set(2.5,1.5,4),t.add(o);const l=new hf(16746598,.6,16);l.position.set(-3,-1,2),t.add(l);const c=new wu(1,7),u=new Kn({uniforms:{uTime:{value:0},uLevel:{value:0},uState:{value:0},uColorA:{value:new Ct(4491519)},uColorB:{value:new Ct(11197951)},cameraPos:{value:new ge}},vertexShader:hR,fragmentShader:pR,transparent:!0,side:oi,depthWrite:!1}),f=new gi(c,u);t.add(f);function h(_){u.uniforms.uState.value=mR[_]??0,_==="speaking"?(u.uniforms.uColorA.value.setHex(16750950),u.uniforms.uColorB.value.setHex(16729088)):_==="processing"?(u.uniforms.uColorA.value.setHex(10053375),u.uniforms.uColorB.value.setHex(6741503)):(u.uniforms.uColorA.value.setHex(4491519),u.uniforms.uColorB.value.setHex(11197951))}function d(_){u.uniforms.uLevel.value=Math.max(0,Math.min(1,_))}function p(){const _=n.clientWidth,O=Math.max(n.clientHeight,1);i.aspect=_/O,i.position.z=a(_,O),i.updateProjectionMatrix(),e.setSize(_,O)}const m=new ResizeObserver(()=>p());m.observe(n),p();function E(_){u.uniforms.uTime.value+=_,u.uniforms.cameraPos.value.copy(i.position),f.rotation.y+=_*.15,e.render(t,i)}function g(){m.disconnect(),c.dispose(),u.dispose(),e.dispose(),e.domElement.parentNode===n&&n.removeChild(e.domElement)}return{setStateName:h,setLevel:d,tick:E,resize:p,dispose:g}}async function _R(n){const e=new OfflineAudioContext(1,1,16e3),t=await n.arrayBuffer(),i=await e.decodeAudioData(t),r=new OfflineAudioContext(1,Math.ceil(i.duration*16e3),16e3),a=r.createBufferSource();a.buffer=i,a.connect(r.destination),a.start();const l=(await r.startRendering()).getChannelData(0),c=new ArrayBuffer(44+l.length*2),u=new DataView(c),f=(h,d)=>{for(let p=0;p<d.length;p++)u.setUint8(h+p,d.charCodeAt(p))};f(0,"RIFF"),u.setUint32(4,36+l.length*2,!0),f(8,"WAVE"),f(12,"fmt "),u.setUint32(16,16,!0),u.setUint16(20,1,!0),u.setUint16(22,1,!0),u.setUint32(24,16e3,!0),u.setUint32(28,32e3,!0),u.setUint16(32,2,!0),u.setUint16(34,16,!0),f(36,"data"),u.setUint32(40,l.length*2,!0);for(let h=0;h<l.length;h++){const d=Math.max(-1,Math.min(1,l[h]));u.setInt16(44+h*2,d<0?d*32768:d*32767,!0)}return new Uint8Array(c)}function vR(){const n=["audio/webm;codecs=opus","audio/webm","audio/ogg;codecs=opus","audio/mp4"];for(const e of n)if(typeof MediaRecorder<"u"&&MediaRecorder.isTypeSupported(e))return e;return""}const Bf=1e3,xR=3e4;function bR(n){let e=null,t=!1,i=Bf,r=null;function a(){if(!t){try{e=new WebSocket(Nc("/ws/voice-state"))}catch{o();return}e.onopen=()=>{var l;i=Bf,(l=n.onOpen)==null||l.call(n)},e.onmessage=l=>{try{const c=JSON.parse(l.data);n.onFrame(c)}catch{}},e.onclose=()=>{var l;(l=n.onClose)==null||l.call(n),o()},e.onerror=()=>{e==null||e.close()}}}function o(){t||(r=setTimeout(()=>{i=Math.min(i*2,xR),a()},i))}return a(),()=>{t=!0,r&&clearTimeout(r),e==null||e.close()}}async function SR(n,e,t={}){const i=new FormData,r=new Uint8Array(n);i.append("audio",new Blob([r.buffer],{type:"audio/wav"}),"voice.wav"),i.append("use_context",t.use_context===!1?"false":"true"),i.append("max_tokens",String(t.max_tokens??512));const a=await fetch(mo+"/voice/interact",{method:"POST",body:i}),o=await a.json().catch(()=>({}));if(!a.ok){const l=o.detail,c=typeof l=="string"?l:`HTTP ${a.status}`;throw new Error(c)}return{transcript:String(o.transcript??"").trim(),session_id:typeof o.session_id=="string"?o.session_id:void 0,assistant_message:String(o.assistant_message??"").trim(),model_used:typeof o.model_used=="string"?o.model_used:void 0,latency_ms:typeof o.latency_ms=="number"?o.latency_ms:void 0,context_sources:Array.isArray(o.context_sources)?o.context_sources:void 0,topic:typeof o.topic=="string"?o.topic:void 0,aegis_flags:Array.isArray(o.aegis_flags)?o.aegis_flags:void 0}}async function yR(n){const e=n.trim();if(!e)return null;const t=await fetch(mo+"/voice/tts?text="+encodeURIComponent(e));if(t.status===404||t.status===501)return null;if(!t.ok)throw new Error(`tts HTTP ${t.status}`);return await t.blob()}var ER=ie('<button class="px-2 py-1.5 rounded-md text-sm font-mono border border-border/60 text-muted hover:text-fg">Cancel</button>'),MR=ie('<div class="h-full w-full flex flex-col relative"><div class="absolute top-2 left-2 right-2 flex items-center justify-between text-xs font-mono z-10"><span> </span> <span class="text-muted/70"> <!> <!></span></div> <div class="flex-1 min-h-0"></div> <div class="border-t border-border/40 px-3 py-2 flex flex-col gap-2 text-xs"><div class="flex items-center gap-2"><button> </button> <!> <span class="text-muted/70 truncate"> </span></div> <p class="text-[10px] text-muted/60 font-mono">Global hotkey: <span class="text-fg">Super+M</span> <!></p></div></div>');function Au(n,e){Mt(e,!1),ft(e,"app",8)();let i=ue(),r=null,a=0,o=0,l=ue("idle"),c=ue(0),u=ue(!1),f=ue(!1),h=ue(!1),d=ue(""),p=ue(""),m=null,E=null,g=[];const _=jn.subscribe(xe=>{W(l,xe),r==null||r.setStateName(xe)}),O=Id.subscribe(xe=>{W(c,xe),r==null||r.setLevel(xe)}),D=Bo.subscribe(xe=>{W(u,xe)});let y=0;const B=ap.subscribe(xe=>{xe!==y&&(y=xe,H())});zt(()=>{r=gR(s(i)),r.setStateName(s(l)),r.setLevel(s(c)),o=performance.now();const xe=_e=>{const De=Math.min(.1,(_e-o)/1e3);o=_e,r==null||r.tick(De),a=requestAnimationFrame(xe)};a=requestAnimationFrame(xe);const Ee=bR({onFrame:_e=>{_e.state&&jn.set(_e.state),typeof _e.audio_level=="number"&&Id.set(_e.audio_level)},onOpen:()=>Bo.set(!0),onClose:()=>Bo.set(!1)});return()=>{Ee()}}),Jt(()=>{_(),O(),D(),B(),cancelAnimationFrame(a),r==null||r.dispose(),m==null||m.getTracks().forEach(xe=>xe.stop()),E=null,g=[]});function R(){return`voice-${Date.now()}-${Math.random().toString(36).slice(2,8)}`}function C(xe){if(typeof window>"u"||!window.speechSynthesis)return;const Ee=xe.trim();if(!Ee)return;window.speechSynthesis.cancel();const _e=new SpeechSynthesisUtterance(Ee);_e.rate=1,window.speechSynthesis.speak(_e)}async function b(xe){jn.set("speaking");try{const Ee=await yR(xe);if(!Ee){C(xe);return}const _e=URL.createObjectURL(Ee),De=new Audio(_e);await De.play().catch(()=>C(xe)),De.onended=()=>URL.revokeObjectURL(_e)}catch{C(xe)}finally{jn.set("idle")}}async function A(){var Ee;if(s(f)||s(h))return;if(!((Ee=navigator.mediaDevices)!=null&&Ee.getUserMedia)){W(d,"Microphone unavailable (HTTPS required on some browsers)"),mt({title:"Voice",body:s(d),kind:"warn",ttlMs:3e3});return}try{m=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:!0,noiseSuppression:!0}})}catch(_e){W(d,`Mic error: ${_e instanceof Error?_e.message:String(_e)}`),mt({title:"Voice",body:s(d),kind:"err",ttlMs:3e3});return}g=[];const xe=vR();W(p,xe||"(browser default)"),E=xe?new MediaRecorder(m,{mimeType:xe}):new MediaRecorder(m),E.ondataavailable=_e=>{_e.data.size>0&&g.push(_e.data)},E.start(250),W(f,!0),W(d,"Listening… press again to send"),jn.set("listening")}async function k(){var Ne;if(!E||!s(f))return;const xe=E;await new Promise(Oe=>{xe.onstop=()=>Oe(),xe.stop()});const Ee=g.slice();g=[],m==null||m.getTracks().forEach(Oe=>Oe.stop()),m=null,E=null,W(f,!1),jn.set("processing"),W(h,!0);const _e=((Ne=Ee[0])==null?void 0:Ne.type)||"audio/webm",De=new Blob(Ee,{type:_e});if(De.size<256){W(d,"Recording too short"),jn.set("idle"),W(h,!1);return}try{const Oe=await _R(De),J=await SR(Oe);Ex({id:R(),transcript:J.transcript,reply:J.assistant_message,model:J.model_used,contextSources:J.context_sources,sessionId:J.session_id,ts:Date.now()}),W(d,J.transcript?`“${J.transcript.slice(0,60)}”`:""),J.assistant_message?await b(J.assistant_message):jn.set("idle")}catch(Oe){W(d,Oe instanceof Error?Oe.message:String(Oe)),mt({title:"Voice error",body:s(d).slice(0,140),kind:"err"}),jn.set("idle")}finally{W(h,!1)}}function z(){!s(f)||!E||(E.onstop=null,E.stop(),g=[],m==null||m.getTracks().forEach(xe=>xe.stop()),m=null,E=null,W(f,!1),W(d,"Cancelled"),jn.set("idle"))}async function H(){s(h)||(s(f)?await k():await A())}function q(xe){switch(xe){case"listening":case"wake_detected":return"bg-accent/20 text-accent";case"processing":return"bg-warn/20 text-warn";case"speaking":return"bg-ok/20 text-ok";default:return"bg-surface-2/70 text-muted"}}wt();var Q=MR(),G=M(Q),T=M(G),w=M(T,!0);S(T);var I=U(T,2),F=M(I),Y=U(F);{var te=xe=>{var Ee=ea("· rec");j(xe,Ee)};Ae(Y,xe=>{s(f)&&xe(te)})}var X=U(Y,2);{var K=xe=>{var Ee=ea("· processing");j(xe,Ee)};Ae(X,xe=>{s(h)&&xe(K)})}S(I),S(G);var se=U(G,2);Er(se,xe=>W(i,xe),()=>s(i));var ne=U(se,2),N=M(ne),V=M(N),re=M(V,!0);S(V);var Me=U(V,2);{var fe=xe=>{var Ee=ER();Re("click",Ee,z),j(xe,Ee)};Ae(Me,xe=>{s(f)&&xe(fe)})}var oe=U(Me,2),ve=M(oe,!0);S(oe),S(N);var ye=U(N,2),Ie=U(M(ye),2),be=U(Ie);{var ke=xe=>{var Ee=ea();me(()=>ee(Ee,`· ${s(p)??""}`)),j(xe,Ee)};Ae(be,xe=>{s(p)&&xe(ke)})}S(ye),S(ne),S(Q),me((xe,Ee)=>{vt(T,1,`px-2 py-0.5 rounded-md ${xe??""}`),ee(w,s(l)),ee(F,`${s(u)?"phaos":"offline"} `),vt(V,1,`px-3 py-1.5 rounded-md text-sm font-mono transition-colors
               ${s(f)?"bg-err/80 text-bg":"bg-accent text-bg"}
               disabled:opacity-50`),V.disabled=s(h),ee(re,s(f)?"■ Stop & Send":"● Push to talk"),ee(ve,s(d)),ee(Ie,` · Level ${Ee??""}% `)},[()=>(s(l),L(()=>q(s(l)))),()=>(s(c),L(()=>Math.round(s(c)*100)))]),Re("click",V,()=>H()),j(n,Q),Tt()}var TR=ie('<div class="h-full w-full flex flex-col items-center justify-center text-center p-6 select-none"><p class="text-4xl mb-3 opacity-60">🪵</p> <h3 class="text-fg text-lg font-mono"> </h3> <p class="text-muted text-sm mt-2 max-w-xs">Not implemented yet. Coming in Phase 2 — drop notes in <code class="text-accent">~/.zeus/zeus-os/apps.json</code> to pin custom entries here.</p></div>');function Ii(n,e){Mt(e,!1);let t=ft(e,"app",8);wt();var i=TR(),r=U(M(i),2),a=M(r,!0);S(r),kn(2),S(i),me(()=>ee(a,(tt(t()),L(()=>t().title)))),j(n,i),Tt()}var wR=ie('<div role="group"><header class="flex items-center justify-between px-3 py-1.5 text-xs select-none" style="background: rgb(var(--surface-2) / 0.75); border-bottom: 1px solid rgb(var(--border-color) / 0.7);"><span class="font-mono truncate text-muted"> </span> <button class="text-muted hover:text-err transition-colors px-1" title="Close" aria-label="Close window">×</button></header> <div class="absolute inset-0" style="top: 28px;"><!></div></div>');function AR(n,e){Mt(e,!1);const t=()=>un(d,"$x",o),i=()=>un(p,"$y",o),r=()=>un(m,"$w",o),a=()=>un(E,"$h",o),[o,l]=ua(),c=ue();let u=ft(e,"leaf",8),f=ft(e,"rect",8),h=ft(e,"focused",8);const d=ps(f().x,{duration:180,easing:si}),p=ps(f().y,{duration:180,easing:si}),m=ps(f().w,{duration:180,easing:si}),E=ps(f().h,{duration:180,easing:si}),g={Terminal:Pc,Chat:Xc,SystemMonitor:qc,FileManager:Yc,Tools:Kc,Jobs:Zc,TokenUsage:Jc,Settings:Qc,Memories:jc,Knowledge:eu,Agents:tu,Ingest:nu,Obsidian:iu,Editor:ru,HomeAssistant:au,Linear:su,Processes:ou,Network:lu,Notepad:cu,Calendar:uu,Images:du,VoiceOrb:Au,Placeholder:Ii};Jt(()=>{}),lt(()=>tt(f()),()=>{d.set(f().x)}),lt(()=>tt(f()),()=>{p.set(f().y)}),lt(()=>tt(f()),()=>{m.set(f().w)}),lt(()=>tt(f()),()=>{E.set(f().h)}),lt(()=>(tt(u()),Ii),()=>{W(c,g[u().app.kind]??Ii)}),Ht(),wt();var _=wR();let O;var D=M(_),y=M(D),B=M(y,!0);S(y);var R=U(y,2);S(D);var C=U(D,2),b=M(C);Mc(b,()=>s(c),(A,k)=>{k(A,{get app(){return tt(u()),L(()=>u().app)}})}),S(C),S(_),me(()=>{O=vt(_,1,"window-shell absolute overflow-hidden",null,O,{focused:h()}),Ln(_,`left:${t()??""}px; top:${i()??""}px; width:${r()??""}px; height:${a()??""}px;`),$t(_,"aria-label",(tt(u()),L(()=>u().app.title))),ee(B,(tt(u()),L(()=>u().app.title)))}),Re("click",R,()=>{Js(u().id),Ha()}),Re("mousedown",_,()=>Js(u().id)),pi(1,_,()=>ho,()=>({duration:200,start:.96,easing:si})),pi(2,_,()=>ts,()=>({duration:120})),j(n,_),Tt(),l()}const er={Meta:"Super",Alt:"Alt",CtrlAlt:"Ctrl+Alt"};function RR(n){const e=n.split("+").map(i=>i.trim()).filter(Boolean);if(!e.length)return null;const t={super:!1,ctrl:!1,alt:!1,shift:!1,key:""};for(const i of e){const r=i.toLowerCase();r==="super"||r==="mod"||r==="meta"||r==="cmd"?t.super=!0:r==="ctrl"||r==="control"?t.ctrl=!0:r==="alt"||r==="option"?t.alt=!0:r==="shift"?t.shift=!0:t.key=Yp(i)}return t.key?t:null}function Yp(n){const e=n.toLowerCase();return{return:"enter",esc:"escape",spc:" ",space:" ",slash:"/"}[e]??e}function CR(n,e,t){let i,r,a;switch(t.modifier){case"Meta":i=n.metaKey,r=!1,a=!1;break;case"Alt":i=n.altKey,r=!1,a=!0;break;case"CtrlAlt":default:i=n.ctrlKey&&n.altKey,r=i,a=i;break}return e.super!==i||!r&&e.ctrl!==n.ctrlKey||!a&&e.alt!==n.altKey||e.shift!==n.shiftKey?!1:Yp(n.key)===e.key}function IR(n){const e=[];for(const[t,i]of Object.entries(n)){const r=RR(t);r&&e.push({spec:t,bind:r,action:i})}return e}const NR={"Super+Return":{kind:"open",appId:"terminal"},"Super+D":{kind:"toggleLauncher"},"Ctrl+Space":{kind:"toggleLauncher"},"Super+Shift+Q":{kind:"close"},"Super+F":{kind:"toggleFloating"},"Super+R":{kind:"cycleTheme"},"Super+Slash":{kind:"cheatsheet"},"Super+M":{kind:"voicePtt"},"Super+H":{kind:"focus",dir:"left"},"Super+J":{kind:"focus",dir:"down"},"Super+K":{kind:"focus",dir:"up"},"Super+L":{kind:"focus",dir:"right"},"Super+Shift+H":{kind:"move",dir:"left"},"Super+Shift+J":{kind:"move",dir:"down"},"Super+Shift+K":{kind:"move",dir:"up"},"Super+Shift+L":{kind:"move",dir:"right"},"Super+V":{kind:"split",dir:"h"},"Super+S":{kind:"split",dir:"v"},"Super+1":{kind:"workspace",id:1},"Super+2":{kind:"workspace",id:2},"Super+3":{kind:"workspace",id:3},"Super+4":{kind:"workspace",id:4},"Super+5":{kind:"workspace",id:5},"Super+6":{kind:"workspace",id:6},"Super+7":{kind:"workspace",id:7},"Super+8":{kind:"workspace",id:8},"Super+9":{kind:"workspace",id:9},"Super+0":{kind:"workspace",id:10},"Super+Shift+1":{kind:"moveToWorkspace",id:1},"Super+Shift+2":{kind:"moveToWorkspace",id:2},"Super+Shift+3":{kind:"moveToWorkspace",id:3},"Super+Shift+4":{kind:"moveToWorkspace",id:4},"Super+Shift+5":{kind:"moveToWorkspace",id:5},"Super+Shift+6":{kind:"moveToWorkspace",id:6},"Super+Shift+7":{kind:"moveToWorkspace",id:7},"Super+Shift+8":{kind:"moveToWorkspace",id:8},"Super+Shift+9":{kind:"moveToWorkspace",id:9},"Super+Shift+0":{kind:"moveToWorkspace",id:10}};var PR=ie('<span class="absolute -mb-3 w-1 h-1 rounded-full bg-accent2"></span>'),LR=ie("<button> <!></button>"),DR=ie('<span title="CPU"><span class="text-accent">CPU</span> </span>'),kR=ie('<span title="Memory"><span class="text-accent">MEM</span> </span>'),UR=ie('<span title="GPU utilization"><span class="text-accent">GPU</span> </span>'),OR=ie('<span title="VRAM used / total"><span class="text-accent">VRAM</span> </span>'),FR=ie(`<header class="surface-blur absolute top-0 left-0 right-0 z-30 flex items-center px-3 select-none" style="height: var(--panel-height);"><div class="flex gap-1.5 items-center"></div> <div class="flex-1 text-center text-xs text-muted truncate px-4"> </div> <div class="flex items-center gap-3 text-xs font-mono text-muted"><!> <!> <!> <!> <span class="px-1.5 py-0.5 rounded-md text-[10px] uppercase tracking-wide text-bg bg-accent2/80" title="WM modifier — open the launcher (Ctrl+Space) and search 'modifier' to change"> </span> <span class="text-fg"> </span></div></header>`);function Kp(n,e){Mt(e,!1);const t=()=>un(Mr,"$activeWorkspace",r),i=()=>un(Un,"$wm",r),[r,a]=ua(),o=ue(),l=ue(),c=ue(),u=ue(),f=ue(),h=ue();let d=ft(e,"modifier",8,"Meta"),p=ue(new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"})),m=null,E=ue(null),g=null;zt(()=>{m=setInterval(()=>{W(p,new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"}))},1e3),g=op(I=>W(E,I))}),Jt(()=>{m&&clearInterval(m),g==null||g.close()}),lt(()=>t(),()=>{W(o,t())}),lt(()=>(s(o),Pi),()=>{var I,F;W(l,(I=s(o))!=null&&I.focusId?((F=Pi(s(o).root,s(o).focusId))==null?void 0:F.app.title)??"":"")}),lt(()=>s(E),()=>{var I;W(c,((I=s(E))==null?void 0:I.cpu_pct)??null)}),lt(()=>s(E),()=>{var I;W(u,(I=s(E))!=null&&I.mem&&s(E).mem.total>0?Math.round((s(E).mem.total-s(E).mem.available)/s(E).mem.total*100):null)}),lt(()=>s(E),()=>{var I,F;W(f,((F=(I=s(E))==null?void 0:I.gpu)==null?void 0:F.util)??null)}),lt(()=>s(E),()=>{var I;W(h,(I=s(E))!=null&&I.gpu&&s(E).gpu.mem_total>0?Math.round(s(E).gpu.mem_used/s(E).gpu.mem_total*100):null)}),Ht(),wt();var _=FR(),O=M(_);ct(O,5,()=>(i(),L(()=>i().workspaces)),I=>I.id,(I,F)=>{var Y=LR();let te;var X=M(Y),K=U(X);{var se=N=>{var V=PR();j(N,V)},ne=nr(()=>(tt(Zu),s(F),i(),L(()=>!Zu(s(F))&&s(F).id!==i().activeWs)));Ae(K,N=>{s(ne)&&N(se)})}S(Y),me(()=>{te=vt(Y,1,"text-xs font-mono w-6 h-5 rounded-md grid place-items-center transition-colors",null,te,{"bg-accent":s(F).id===i().activeWs,"text-bg":s(F).id===i().activeWs,"text-muted":s(F).id!==i().activeWs}),$t(Y,"title",`Workspace ${s(F),L(()=>s(F).id)??""}`),ee(X,`${s(F),L(()=>s(F).id===10?"0":s(F).id)??""} `)}),Re("click",Y,()=>Cc(s(F).id)),j(I,Y)}),S(O);var D=U(O,2),y=M(D,!0);S(D);var B=U(D,2),R=M(B);{var C=I=>{var F=DR(),Y=U(M(F));S(F),me(te=>ee(Y,` ${te??""}%`),[()=>(s(c),L(()=>s(c).toFixed(0)))]),j(I,F)};Ae(R,I=>{s(c)!==null&&I(C)})}var b=U(R,2);{var A=I=>{var F=kR(),Y=U(M(F));S(F),me(()=>ee(Y,` ${s(u)??""}%`)),j(I,F)};Ae(b,I=>{s(u)!==null&&I(A)})}var k=U(b,2);{var z=I=>{var F=UR(),Y=U(M(F));S(F),me(te=>ee(Y,` ${te??""}%`),[()=>(s(f),L(()=>s(f).toFixed(0)))]),j(I,F)};Ae(k,I=>{s(f)!==null&&I(z)})}var H=U(k,2);{var q=I=>{var F=OR(),Y=U(M(F));S(F),me(()=>ee(Y,` ${s(h)??""}%`)),j(I,F)};Ae(H,I=>{s(h)!==null&&I(q)})}var Q=U(H,2),G=M(Q,!0);S(Q);var T=U(Q,2),w=M(T,!0);S(T),S(B),S(_),me(()=>{ee(y,s(l)),ee(G,(tt(er),tt(d()),L(()=>er[d()]))),ee(w,s(p))}),j(n,_),Tt(),a()}var BR=ie('<div role="group"><header class="flex items-center justify-between px-3 py-1.5 text-xs select-none cursor-move" style="background: rgb(var(--surface-2) / 0.78); border-bottom: 1px solid rgb(var(--border-color) / 0.7); height: 28px;"><span class="font-mono truncate text-muted"> </span> <button class="text-muted hover:text-err px-1" aria-label="Close window" title="Close">×</button></header> <div class="absolute inset-0" style="top: 28px;"><!></div> <span class="absolute left-0 right-0 top-0 h-1 cursor-n-resize z-10"></span> <span class="absolute left-0 right-0 bottom-0 h-1 cursor-s-resize z-10"></span> <span class="absolute left-0 top-0 bottom-0 w-1 cursor-w-resize z-10"></span> <span class="absolute right-0 top-0 bottom-0 w-1 cursor-e-resize z-10"></span> <span class="absolute left-0 top-0 w-3 h-3 cursor-nw-resize z-20"></span> <span class="absolute right-0 top-0 w-3 h-3 cursor-ne-resize z-20"></span> <span class="absolute left-0 bottom-0 w-3 h-3 cursor-sw-resize z-20"></span> <span class="absolute right-0 bottom-0 w-3 h-3 cursor-se-resize z-20"></span></div>');function zR(n,e){Mt(e,!1);const t=()=>un(da,"$viewport",i),[i,r]=ua(),a=ue();let o=ft(e,"win",8),l=ft(e,"focused",8);const c={Terminal:Pc,Chat:Xc,SystemMonitor:qc,FileManager:Yc,Tools:Kc,Jobs:Zc,TokenUsage:Jc,Settings:Qc,Memories:jc,Knowledge:eu,Agents:tu,Ingest:nu,Obsidian:iu,Editor:ru,HomeAssistant:au,Linear:su,Processes:ou,Network:lu,Notepad:cu,Calendar:uu,Images:du,VoiceOrb:Au,Placeholder:Ii},u=280,f=180;let h=null;function d(T,w){const I=w.x+w.w-60,F=w.x-T.w+60,Y=w.y,te=w.y+w.h-40;return{x:Math.min(I,Math.max(F,T.x)),y:Math.min(te,Math.max(Y,T.y)),w:Math.max(u,T.w),h:Math.max(f,T.h)}}function p(T,w){if(w.button!==0)return;w.preventDefault(),Ju(o().id),h={mode:T,startX:w.clientX,startY:w.clientY,startRect:{x:o().x,y:o().y,w:o().w,h:o().h}},w.target.setPointerCapture(w.pointerId)}function m(T){if(!h)return;const w=T.clientX-h.startX,I=T.clientY-h.startY,F={...h.startRect};switch(h.mode){case"move":F.x+=w,F.y+=I;break;case"e":F.w+=w;break;case"s":F.h+=I;break;case"w":F.x+=w,F.w-=w;break;case"n":F.y+=I,F.h-=I;break;case"se":F.w+=w,F.h+=I;break;case"sw":F.x+=w,F.w-=w,F.h+=I;break;case"ne":F.y+=I,F.w+=w,F.h-=I;break;case"nw":F.x+=w,F.y+=I,F.w-=w,F.h-=I;break}const Y=d(F,t());Mg(o().id,Y)}function E(T){if(!h)return;const w=T.target;try{w.releasePointerCapture(T.pointerId)}catch{}h=null}lt(()=>(tt(o()),Ii),()=>{W(a,c[o().app.kind]??Ii)}),Ht(),wt();var g=BR();let _;var O=M(g),D=M(O),y=M(D,!0);S(D);var B=U(D,2);S(O);var R=U(O,2),C=M(R);Mc(C,()=>s(a),(T,w)=>{w(T,{get app(){return tt(o()),L(()=>o().app)}})}),S(R);var b=U(R,2),A=U(b,2),k=U(A,2),z=U(k,2),H=U(z,2),q=U(H,2),Q=U(q,2),G=U(Q,2);S(g),me(()=>{_=vt(g,1,"window-shell absolute overflow-hidden",null,_,{focused:l()}),Ln(g,`left:${tt(o()),L(()=>o().x)??""}px; top:${tt(o()),L(()=>o().y)??""}px; width:${tt(o()),L(()=>o().w)??""}px; height:${tt(o()),L(()=>o().h)??""}px; z-index:${tt(o()),L(()=>50+o().z)??""};`),$t(g,"aria-label",(tt(o()),L(()=>o().app.title))),ee(y,(tt(o()),L(()=>o().app.title)))}),Re("click",B,ah(()=>Tg(o().id))),Re("pointerdown",O,T=>p("move",T)),Re("pointermove",O,m),Re("pointerup",O,E),Re("pointercancel",O,E),Re("pointerdown",b,T=>p("n",T)),Re("pointermove",b,m),Re("pointerup",b,E),Re("pointercancel",b,E),Re("pointerdown",A,T=>p("s",T)),Re("pointermove",A,m),Re("pointerup",A,E),Re("pointercancel",A,E),Re("pointerdown",k,T=>p("w",T)),Re("pointermove",k,m),Re("pointerup",k,E),Re("pointercancel",k,E),Re("pointerdown",z,T=>p("e",T)),Re("pointermove",z,m),Re("pointerup",z,E),Re("pointercancel",z,E),Re("pointerdown",H,T=>p("nw",T)),Re("pointermove",H,m),Re("pointerup",H,E),Re("pointercancel",H,E),Re("pointerdown",q,T=>p("ne",T)),Re("pointermove",q,m),Re("pointerup",q,E),Re("pointercancel",q,E),Re("pointerdown",Q,T=>p("sw",T)),Re("pointermove",Q,m),Re("pointerup",Q,E),Re("pointercancel",Q,E),Re("pointerdown",G,T=>p("se",T)),Re("pointermove",G,m),Re("pointerup",G,E),Re("pointercancel",G,E),Re("mousedown",g,()=>Ju(o().id)),pi(1,g,()=>ho,()=>({duration:200,start:.94,easing:si})),pi(2,g,()=>ts,()=>({duration:120})),j(n,g),Tt(),r()}var HR=ie('<div class="absolute inset-0 flex items-center justify-center pointer-events-none"><div class="text-center select-none"><p class="text-fg/30 text-2xl font-mono"> </p> <p class="text-muted/60 text-sm mt-2"><kbd class="font-mono">Super</kbd> + <kbd class="font-mono">Return</kbd> &nbsp;Terminal &nbsp;·&nbsp; <kbd class="font-mono">Super</kbd> + <kbd class="font-mono">D</kbd> &nbsp;Launcher</p></div></div>'),GR=ie('<div class="absolute inset-0"><!> <!> <!></div>'),VR=ie('<div class="relative h-full w-full overflow-hidden"><!> <!></div>');function WR(n,e){Mt(e,!1);const t=()=>un(ns,"$gap",l),i=()=>un(Mr,"$activeWorkspace",l),r=()=>un(uh,"$leaves",l),a=()=>un(_g,"$rects",l),o=()=>un(vg,"$floating",l),[l,c]=ua();let u=ft(e,"modifier",8,"Meta"),f=ue();function h(){if(!s(f))return;const E=s(f).getBoundingClientRect(),g=30,_=t();da.set({x:_,y:g+_,w:Math.max(0,E.width-_*2),h:Math.max(0,E.height-g-_*2)})}zt(()=>{h();const E=new ResizeObserver(h);return s(f)&&E.observe(s(f)),()=>E.disconnect()}),wt();var d=VR(),p=M(d);Kp(p,{get modifier(){return u()}});var m=U(p,2);qm(m,()=>(i(),L(()=>i().id)),E=>{var g=GR(),_=M(g);ct(_,1,r,B=>B.id,(B,R)=>{var C=Ai(),b=Pt(C);{var A=k=>{{let z=tr(()=>(s(R),i(),L(()=>s(R).id===i().focusId)));AR(k,{get leaf(){return s(R)},get rect(){return a(),s(R),L(()=>a()[s(R).id])},get focused(){return s(z)}})}};Ae(b,k=>{a(),s(R),L(()=>a()[s(R).id])&&k(A)})}j(B,C)});var O=U(_,2);ct(O,1,o,B=>B.id,(B,R)=>{{let C=tr(()=>(s(R),i(),L(()=>s(R).id===i().focusId)));zR(B,{get win(){return s(R)},get focused(){return s(C)}})}});var D=U(O,2);{var y=B=>{var R=HR(),C=M(R),b=M(C),A=M(b);S(b),kn(2),S(C),S(R),me(()=>ee(A,`Workspace ${i(),L(()=>i().id)??""}`)),j(B,R)};Ae(D,B=>{r(),o(),L(()=>r().length===0&&o().length===0)&&B(y)})}S(g),pi(1,g,()=>ts,()=>({duration:200,easing:si})),j(E,g)}),S(d),Er(d,E=>W(f,E),()=>s(f)),j(n,d),Tt(),c()}var $R=ie('<div class="absolute inset-0" style="top: 30px; bottom: 56px;"><div class="window-shell focused absolute inset-2 overflow-hidden"><header class="flex items-center justify-between px-3 py-1.5 text-xs" style="background: rgb(var(--surface-2) / 0.75); border-bottom: 1px solid rgb(var(--border-color) / 0.7);"><span class="font-mono truncate"> </span> <button class="text-muted hover:text-err">×</button></header> <div class="absolute inset-0" style="top: 28px;"><!></div></div></div>'),XR=ie('<div class="absolute inset-0 grid place-items-center text-muted text-sm">Tap the + button to open an app.</div>'),qR=ie("<button></button>"),YR=ie('<div class="relative h-full w-full flex flex-col"><!> <div class="flex-1 overflow-hidden mt-[30px]"><!></div> <nav class="surface-blur absolute bottom-0 left-0 right-0 flex items-center justify-between px-3" style="height: 56px;"><button class="text-fg/80 text-xl px-3" aria-label="Previous window">‹</button> <div class="flex gap-1.5"></div> <button class="text-fg/80 text-xl px-3" aria-label="Next window">›</button></nav></div>');function KR(n,e){Mt(e,!1);const t=()=>un(uh,"$leaves",a),i=()=>un(Mr,"$activeWorkspace",a),r=()=>un(Un,"$wm",a),[a,o]=ua(),l=ue(),c=ue(),u=ue();let f=ft(e,"modifier",8,"Meta");const h={Terminal:Pc,Chat:Xc,SystemMonitor:qc,FileManager:Yc,Tools:Kc,Jobs:Zc,TokenUsage:Jc,Settings:Qc,Memories:jc,Knowledge:eu,Agents:tu,Ingest:nu,Obsidian:iu,Editor:ru,HomeAssistant:au,Linear:su,Processes:ou,Network:lu,Notepad:cu,Calendar:uu,Images:du,VoiceOrb:Au,Placeholder:Ii};function d(C){if(!t().length)return;const b=(t().length+(s(l)<0?0:s(l))+C)%t().length;Js(t()[b].id)}lt(()=>(t(),i()),()=>{W(l,t().findIndex(C=>C.id===i().focusId))}),lt(()=>(s(l),t()),()=>{W(c,s(l)>=0?t()[s(l)]:t()[0])}),lt(()=>(s(c),Ii),()=>{W(u,s(c)?h[s(c).app.kind]??Ii:null)}),Ht(),wt();var p=YR(),m=M(p);Kp(m,{get modifier(){return f()}});var E=U(m,2),g=M(E);{var _=C=>{var b=$R(),A=M(b),k=M(A),z=M(k),H=M(z,!0);S(z);var q=U(z,2);S(k);var Q=U(k,2),G=M(Q);Mc(G,()=>s(u),(T,w)=>{w(T,{get app(){return s(c),L(()=>s(c).app)}})}),S(Q),S(A),S(b),me(()=>ee(H,(s(c),L(()=>s(c).app.title)))),Re("click",q,function(...T){Ha==null||Ha.apply(this,T)}),j(C,b)},O=C=>{var b=XR();j(C,b)};Ae(g,C=>{s(c)&&s(u)?C(_):C(O,-1)})}S(E);var D=U(E,2),y=M(D),B=U(y,2);ct(B,5,()=>(r(),L(()=>r().workspaces)),C=>C.id,(C,b)=>{var A=qR();let k;me(()=>{k=vt(A,1,"w-2.5 h-2.5 rounded-full",null,k,{"bg-accent":s(b).id===r().activeWs,"bg-muted":s(b).id!==r().activeWs}),$t(A,"aria-label",`Workspace ${s(b),L(()=>s(b).id)??""}`)}),Re("click",A,()=>Cc(s(b).id)),j(C,A)}),S(B);var R=U(B,2);S(D),S(p),Re("click",y,()=>d(-1)),Re("click",R,()=>d(1)),j(n,p),Tt(),o()}function Zp(){return dt("/zeus-os/apps")}const Ga=[{id:"catppuccin-mocha",label:"Catppuccin Mocha",preview:{bg:"#1e1e2e",accent:"#89b4fa"}},{id:"tokyo-night",label:"Tokyo Night",preview:{bg:"#1a1b26",accent:"#7aa2f7"}},{id:"gruvbox-dark",label:"Gruvbox Dark",preview:{bg:"#282828",accent:"#fabd2f"}}];function Va(n){typeof document<"u"&&(document.documentElement.dataset.theme=n)}function ZR(n){const e=Ga.findIndex(t=>t.id===n);return Ga[(e+1)%Ga.length].id}var JR=ie('<li><button><span> </span> <span class="text-xs opacity-60"> </span></button></li>'),QR=ie('<li class="px-4 py-6 text-center text-muted text-sm">No matches.</li>'),jR=ie('<div class="absolute inset-0 z-40 flex items-start justify-center pt-[15vh]" style="background: rgb(0 0 0 / 0.35); backdrop-filter: blur(6px);" role="presentation"><div class="surface-blur rounded-2xl shadow-2xl w-[min(640px,92vw)] overflow-hidden border border-border/40"><div class="p-3 border-b border-border/40"><input placeholder="Search apps, themes, actions…" class="w-full bg-transparent text-fg placeholder:text-muted/70 outline-none text-base font-mono"/></div> <ul class="max-h-[50vh] overflow-y-auto"></ul> <footer class="px-4 py-2 text-[10px] text-muted border-t border-border/40 flex justify-between"><span><kbd>↑</kbd>/<kbd>↓</kbd> select &nbsp; <kbd>↵</kbd> open &nbsp; <kbd>Esc</kbd> close &nbsp;·&nbsp; modifier: <span class="text-fg"> </span></span> <span> </span></footer></div></div>');function eC(n,e){Mt(e,!1);const t=ue(),i=ue(),r=ue(),a=ue(),o=ue(),l=ue();let c=ft(e,"open",12,!1),u=ft(e,"modifier",8,"Meta");const f=jp();let h=ue(""),d=ue(),p=ue([]),m=ue(0);const E=["Meta","Alt","CtrlAlt"];function g(C,b){const A=b.trim().toLowerCase();if(!A)return C;const k=z=>{const H=z.toLowerCase();if(H.startsWith(A))return 0;if(H.includes(A))return 1;let q=0;for(const Q of H)q<A.length&&Q===A[q]&&(q+=1);return q===A.length?2:3};return C.map(z=>({it:z,s:k(z.label)})).filter(z=>z.s<3).sort((z,H)=>z.s-H.s).map(z=>z.it)}async function _(){try{const{apps:C}=await Zp();W(p,C)}catch{W(p,[])}}function O(C){const b=s(l)[C];b&&(b.onPick(),c(!1))}function D(C){c()&&(C.key==="Escape"?c(!1):C.key==="ArrowDown"?(C.preventDefault(),W(m,(s(m)+1)%Math.max(1,s(l).length))):C.key==="ArrowUp"?(C.preventDefault(),W(m,(s(m)-1+s(l).length)%Math.max(1,s(l).length))):C.key==="Enter"&&(C.preventDefault(),O(s(m))))}lt(()=>(s(p),gr),()=>{W(t,s(p).map(C=>({id:"app:"+C.id,label:C.title,hint:"app",onPick:()=>{gr({appId:C.id,kind:C.kind,title:C.title})}})))}),lt(()=>Va,()=>{W(i,Ga.map(C=>({id:"theme:"+C.id,label:"Theme: "+C.label,hint:"theme",onPick:()=>Va(C.id)})))}),lt(()=>(tt(u()),er),()=>{W(r,E.filter(C=>C!==u()).map(C=>({id:"modifier:"+C,label:`Modifier: ${er[C]}${C==="CtrlAlt"?" (Windows-friendly)":C==="Meta"?" (Linux default)":""}`,hint:"modifier",onPick:()=>f("setModifier",C)})))}),lt(()=>{},()=>{W(a,[{id:"action:reload",label:"Reload Zeus OS",hint:"action",onPick:()=>window.location.reload()}])}),lt(()=>(s(t),s(i),s(r),s(a)),()=>{W(o,[...s(t),...s(i),...s(r),...s(a)])}),lt(()=>(tt(c()),s(d)),()=>{c()&&(_(),W(h,""),W(m,0),vr().then(()=>{var C;return(C=s(d))==null?void 0:C.focus()}))}),lt(()=>(s(o),s(h)),()=>{W(l,g(s(o),s(h)))}),Ht(),wt();var y=Ai();Re("keydown",Qf,D);var B=Pt(y);{var R=C=>{var b=jR(),A=M(b),k=M(A),z=M(k);gn(z),Er(z,F=>W(d,F),()=>s(d)),S(k);var H=U(k,2);ct(H,7,()=>s(l),F=>F.id,(F,Y,te)=>{var X=JR(),K=M(X);let se;var ne=M(K),N=M(ne,!0);S(ne);var V=U(ne,2),re=M(V,!0);S(V),S(K),S(X),me(()=>{se=vt(K,1,"w-full text-left px-4 py-2 flex items-center justify-between text-sm font-mono",null,se,{"bg-accent":s(te)===s(m),"text-bg":s(te)===s(m),"text-fg":s(te)!==s(m)}),ee(N,(s(Y),L(()=>s(Y).label))),ee(re,(s(Y),L(()=>s(Y).hint)))}),Re("mouseenter",K,()=>W(m,s(te))),Re("click",K,()=>O(s(te))),j(F,X)},F=>{var Y=QR();j(F,Y)}),S(H);var q=U(H,2),Q=M(q),G=U(M(Q),8),T=M(G,!0);S(G),S(Q);var w=U(Q,2),I=M(w);S(w),S(q),S(A),S(b),me(()=>{ee(T,(tt(er),tt(u()),L(()=>er[u()]))),ee(I,`${s(l),L(()=>s(l).length)??""} / ${s(o),L(()=>s(o).length)??""}`)}),nn(z,()=>s(h),F=>W(h,F)),Re("input",z,()=>W(m,0)),pi(3,A,()=>ho,()=>({duration:220,start:.96,easing:si})),Re("click",b,rh(()=>c(!1))),pi(3,b,()=>ts,()=>({duration:120})),j(C,b)};Ae(B,C=>{c()&&C(R)})}j(n,y),Tt()}var tC=ie('<tr><td class="py-1 pr-6 text-muted whitespace-nowrap"> </td><td class="py-1 text-fg"> </td></tr>'),nC=ie('<div class="absolute inset-0 z-40 flex items-center justify-center" style="background: rgb(0 0 0 / 0.4); backdrop-filter: blur(6px);" role="presentation"><div class="surface-blur rounded-2xl shadow-2xl w-[min(560px,92vw)] border border-border/40 p-6"><h2 class="text-lg font-mono mb-1 text-accent">Zeus OS — keybinds</h2> <p class="text-xs text-muted mb-3 font-mono">Modifier: <span class="text-fg"> </span> · change it from the launcher (search "modifier")</p> <table class="w-full text-sm font-mono"><tbody></tbody></table> <p class="mt-4 text-xs text-muted">Press <kbd>Esc</kbd> or click outside to dismiss.</p></div></div>');function iC(n,e){Mt(e,!1);const t=ue(),i=ue();let r=ft(e,"open",12,!1),a=ft(e,"modifier",8,"Meta");lt(()=>tt(a()),()=>{W(t,er[a()])}),lt(()=>s(t),()=>{W(i,[[`${s(t)} + Return`,"Open Terminal"],[`${s(t)} + D  /  Ctrl + Space`,"Launcher"],[`${s(t)} + Shift + Q`,"Close window"],[`${s(t)} + F`,"Toggle floating"],[`${s(t)} + H / J / K / L`,"Focus left / down / up / right"],[`${s(t)} + Shift + H / J / K / L`,"Move window"],[`${s(t)} + V / S`,"Split vertical / horizontal"],[`${s(t)} + 1..0`,"Switch workspace"],[`${s(t)} + Shift + 1..0`,"Move window to workspace"],[`${s(t)} + R`,"Cycle theme"],[`${s(t)} + /`,"This cheatsheet"]])}),Ht(),wt();var o=Ai(),l=Pt(o);{var c=u=>{var f=nC(),h=M(f),d=U(M(h),2),p=U(M(d)),m=M(p,!0);S(p),kn(),S(d);var E=U(d,2),g=M(E);ct(g,5,()=>s(i),$n,(_,O)=>{var D=nr(()=>jf(s(O),2));let y=()=>s(D)[0],B=()=>s(D)[1];var R=tC(),C=M(R),b=M(C,!0);S(C);var A=U(C),k=M(A,!0);S(A),S(R),me(()=>{ee(b,y()),ee(k,B())}),j(_,R)}),S(g),S(E),kn(2),S(h),S(f),me(()=>ee(m,s(t))),pi(3,h,()=>ho,()=>({duration:220,start:.96,easing:si})),Re("click",f,rh(()=>r(!1))),pi(3,f,()=>ts,()=>({duration:120})),j(u,f)};Ae(l,u=>{r()&&u(c)})}j(n,o),Tt()}var rC=ie('<p class="text-xs text-muted mt-1 leading-snug"> </p>'),aC=ie('<button type="button" style="background: rgb(var(--surface) / 0.92);"><p class="font-mono text-fg leading-tight"> </p> <!></button>'),sC=ie('<div class="absolute top-12 right-3 z-50 flex flex-col gap-2 pointer-events-none w-72" aria-live="polite" aria-atomic="false"></div>');function oC(n,e){Mt(e,!1);const t=()=>un(Ic,"$toasts",i),[i,r]=ua(),a={info:"border-l-accent",ok:"border-l-ok",warn:"border-l-warn",err:"border-l-err"};wt();var o=sC();ct(o,5,t,l=>l.id,(l,c)=>{var u=aC(),f=M(u),h=M(f,!0);S(f);var d=U(f,2);{var p=m=>{var E=rC(),g=M(E,!0);S(E),me(()=>ee(g,s(c).body)),j(m,E)};Ae(d,m=>{s(c).body&&m(p)})}S(u),me(()=>{vt(u,1,`surface-blur text-left text-sm rounded-wm shadow-lg p-3 pointer-events-auto border border-border/40 border-l-4 ${a[s(c).kind]??""}`),ee(h,s(c).title)}),Re("click",u,()=>dh(s(c).id)),pi(3,u,()=>ug,()=>({x:280,duration:200,easing:si})),j(l,u)}),S(o),j(n,o),Tt(),r()}function lC(){return dt("/zeus-os/config")}function zf(n){return dt("/zeus-os/config",{method:"PUT",body:JSON.stringify(n)})}var cC=ie('<div class="h-screen w-screen overflow-hidden"><!> <!> <!> <!></div>');function vC(n,e){Mt(e,!1);const t=ue();let i=ue(!1),r=ue(!1),a=ue(!1),o="catppuccin-mocha",l=ue(f()),c=null,u=[];function f(){if(typeof navigator>"u")return"Meta";const z=navigator.userAgent||"";return/Windows/i.test(z)?"CtrlAlt":"Meta"}const h=IR(NR);function d(){W(a,typeof window<"u"&&window.innerWidth<768)}function p(){d()}function m(z){const H=z.target;if(H){const q=H.tagName;if((q==="INPUT"||q==="TEXTAREA"||H.isContentEditable)&&!z.metaKey&&!z.altKey)return}for(const q of h)if(CR(z,q.bind,s(t))){z.preventDefault(),g(q.action);return}}function E(z){return u.find(H=>H.id===z)}function g(z){switch(z.kind){case"open":{const H=E(z.appId);H&&gr({appId:H.id,kind:H.kind,title:H.title},z.dir??"h");break}case"close":Ha();break;case"focus":bg(z.dir);break;case"move":Sg(z.dir);break;case"split":{const H=E("terminal");H&&gr({appId:H.id,kind:H.kind,title:H.title},z.dir);break}case"workspace":Cc(z.id);break;case"moveToWorkspace":xg(z.id);break;case"toggleLauncher":W(r,!1),W(i,!s(i));break;case"cycleTheme":{o=ZR(o),Va(o),_(),mt({title:"Theme",body:o,kind:"info",ttlMs:1800});break}case"setTheme":o=z.theme,Va(o),_(),mt({title:"Theme",body:o,kind:"info",ttlMs:1800});break;case"setModifier":W(l,z.mode),O(),mt({title:"Modifier",body:`${er[s(l)]} now stands in for Super`,kind:"ok",ttlMs:2400});break;case"cheatsheet":W(i,!1),W(r,!s(r));break;case"reload":window.location.reload();break;case"toggleFloating":Eg();break;case"voicePtt":{const H=E("voice");if(H){const q=new Set;for(const Q of qn(Un).workspaces){for(const G of Zs(Q.root))q.add(G.app.appId);for(const G of Q.floating)q.add(G.app.appId)}q.has(H.id)||gr({appId:H.id,kind:H.kind,title:H.title},"h")}Mx();break}}}async function _(){if(c){c={...c,theme:o};try{await zf(c)}catch{}}}async function O(){if(c){c={...c,theme:o,modifier:s(l)};try{await zf(c)}catch{}}}async function D(){d(),window.addEventListener("resize",p),window.addEventListener("keydown",m);try{u=(await Zp()).apps}catch{u=[]}try{c=await lC(),c!=null&&c.theme&&Ga.some(H=>H.id===c.theme)&&(o=c.theme,Va(o)),((c==null?void 0:c.modifier)==="Alt"||(c==null?void 0:c.modifier)==="CtrlAlt"||(c==null?void 0:c.modifier)==="Meta")&&W(l,c.modifier)}catch{}const z=E("chat");z&&wg([{app:{appId:z.id,kind:z.kind,title:z.title},workspace:1}])}zt(D),Jt(()=>{window.removeEventListener("resize",p),window.removeEventListener("keydown",m)}),lt(()=>s(l),()=>{W(t,{modifier:s(l)})}),Ht(),wt();var y=cC(),B=M(y);{var R=z=>{KR(z,{get modifier(){return s(l)}})},C=z=>{WR(z,{get modifier(){return s(l)}})};Ae(B,z=>{s(a)?z(R):z(C,-1)})}var b=U(B,2);eC(b,{get modifier(){return s(l)},get open(){return s(i)},set open(z){W(i,z)},$$events:{setModifier:z=>g({kind:"setModifier",mode:z.detail})},$$legacy:!0});var A=U(b,2);iC(A,{get modifier(){return s(l)},get open(){return s(r)},set open(z){W(r,z)},$$legacy:!0});var k=U(A,2);oC(k,{}),S(y),j(n,y),Tt()}export{vC as component};
