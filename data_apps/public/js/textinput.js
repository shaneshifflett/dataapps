function changeLengths(){
    superscript_elem = document.getElementById('id_superscript');
    if(superscript_elem != null){
        superscript_elem.className = '';
        superscript_elem.style.width = '50em';    	
    }

    title_elem = document.getElementById('id_title');
    if(title_elem != null){
        title_elem.className = '';
        title_elem.style.width = '50em';
    }

    slug_elem = document.getElementById('id_slug');
    if(slug_elem != null){
        slug_elem.className = '';
        slug_elem.style.width = '50em';    	
    }
    
    subscript_elem = document.getElementById('id_subscript');
    if(subscript_elem != null){
        subscript_elem.className = '';
        subscript_elem.style.width = '50em';    	
    }
};

(function(i) {var u =navigator.userAgent;var e=/*@cc_on!@*/false; var st =
setTimeout;if(/webkit/i.test(u)){st(function(){var dr=document.readyState;
if(dr=="loaded"||dr=="complete"){i()}else{st(arguments.callee,10);}},10);}
else if((/mozilla/i.test(u)&&!/(compati)/.test(u)) || (/opera/i.test(u))){
document.addEventListener("DOMContentLoaded",i,false); } else if(e){     (
function(){var t=document.createElement('doc:rdy');try{t.doScroll('left');
i();t=null;}catch(e){st(arguments.callee,0);}})();}else{window.onload=i;}})(changeLengths);