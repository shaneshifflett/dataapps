tinyMCEPopup.requireLangPack();
var selNode;

var BayCitizenImg = {
	/*init : function() {
		
	},*/

	insert : function(url) {
		// Insert the contents from the input into the document
		
		
		tinyMCEPopup.editor.execCommand('mceInsertContent', false, "<img src='"+url+"'>");
		tinyMCEPopup.close();

		return;

		comment = tinyMCE.get('in_image');
		comment = comment.getContent();
		comment = comment.replace(/\+/g, "&#43");
		comment = comment.replace(/\\/g, "&#92");
		comment = escape(comment);
	
		var inst = tinyMCEPopup.editor;
		var elm;

		elm = inst.selection.getNode();
		elm = inst.dom.getParent(elm, "SPAN");

		//tinyMCEPopup.editor.execCommand('mceSelectNode',false,selNode);
		if(elm == null){
			tinyMCEPopup.editor.execCommand('mceInsertContent', false, "<span class='annotation' style='text-decoration:underline;' title=\""+comment+"\">"+document.forms[0].in_selected.value+"</span>");
		}
		else{
			//alert('elm exists');
			setAttrib(elm, 'title', comment);
		}
		tinyMCEPopup.close();
		//selNode = {};
	}
};


/*
function setAttrib(elm, attrib, value) {
	var formObj = document.forms[0];
	var valueElm = formObj.elements[attrib.toLowerCase()];
	var dom = tinyMCEPopup.editor.dom;

	if (typeof(value) == "undefined" || value == null) {
		value = "";

		if (valueElm)
			value = valueElm.value;
	}

	// Clean up the style
	if (attrib == 'style')
		value = dom.serializeStyle(dom.parseStyle(value), 'a');

	dom.setAttrib(elm, attrib, value);
}

tinyMCEPopup.onInit.add(BayCitizenImg.init, BayCitizenImg);
*/
