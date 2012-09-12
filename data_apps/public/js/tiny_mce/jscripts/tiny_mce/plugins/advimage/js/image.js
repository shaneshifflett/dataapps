var BayCitizenImg = {
	insert : function(url,alt,caption,credit) {
		document.getElementById("src").value=url;
		//alt is alt
		//title is caption
		//longdesc is credit
		if(alt)document.getElementById("alt").value=alt;
		if(caption)document.getElementById("title").value=caption;
		if(credit)document.getElementById("longdesc").value=credit;
		ImageDialog.showPreviewImage(url, 1);
		mcTabs.displayTab('appearance_tab','appearance_panel');
	}
}

var ImageDialog = {
	preInit : function() {
		var url;

		tinyMCEPopup.requireLangPack();

		if (url = tinyMCEPopup.getParam("external_image_list_url"))
			document.write('<script language="javascript" type="text/javascript" src="' + tinyMCEPopup.editor.documentBaseURI.toAbsolute(url) + '"></script>');
	},

	init : function(ed) {
		mcTabs.displayTab('browse_tab','browse_panel');

		var f = document.forms[0], nl = f.elements, ed = tinyMCEPopup.editor, dom = ed.dom, n = ed.selection.getNode();

		tinyMCEPopup.resizeToInnerSize();
		this.fillClassList('class_list');
		this.fillFileList('src_list', 'tinyMCEImageList');
		this.fillFileList('over_list', 'tinyMCEImageList');
		this.fillFileList('out_list', 'tinyMCEImageList');
		TinyMCE_EditableSelects.init();

		if (n.nodeName == 'IMG') {
			nl.src.value = dom.getAttrib(n, 'src');
			nl.width.value = dom.getAttrib(n, 'width');
			nl.height.value = dom.getAttrib(n, 'height');
			nl.alt.value = dom.getAttrib(n, 'alt');
			nl.title.value = dom.getAttrib(n, 'title');
			nl.longdesc.value = dom.getAttrib(n, 'longdesc');
			nl.topmargin.value = this.getAttrib(n, 'topmargin');
			nl.bottommargin.value = this.getAttrib(n, 'bottommargin');
			nl.leftmargin.value = this.getAttrib(n, 'leftmargin');
			nl.rightmargin.value = this.getAttrib(n, 'rightmargin');
			nl.border.value = this.getAttrib(n, 'border');
			selectByValue(f, 'align', this.getAttrib(n, 'align'));
			selectByValue(f, 'class_list', dom.getAttrib(n, 'class'), true, true);
			nl.style.value = dom.getAttrib(n, 'style');
			nl.id.value = dom.getAttrib(n, 'id');
			nl.dir.value = dom.getAttrib(n, 'dir');
			nl.lang.value = dom.getAttrib(n, 'lang');
			nl.usemap.value = dom.getAttrib(n, 'usemap');
			nl.longdesc.value = dom.getAttrib(n, 'longdesc');
			nl.insert.value = ed.getLang('update');

			if (/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/.test(dom.getAttrib(n, 'onmouseover')))
				nl.onmouseoversrc.value = dom.getAttrib(n, 'onmouseover').replace(/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/, '$1');

			if (/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/.test(dom.getAttrib(n, 'onmouseout')))
				nl.onmouseoutsrc.value = dom.getAttrib(n, 'onmouseout').replace(/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/, '$1');

			if (ed.settings.inline_styles) {
				// Move attribs to styles
				if (dom.getAttrib(n, 'align'))
					this.updateStyle('align');

				if (dom.getAttrib(n, 'topmargin'))
					this.updateStyle('topmargin');
				
				if (dom.getAttrib(n, 'bottommargin'))
                    this.updateStyle('bottommargin');
                   
                if (dom.getAttrib(n, 'leftmargin'))
                    this.updateStyle('leftmargin');
                
                if (dom.getAttrib(n, 'rightmargin'))
                    this.updateStyle('rightmargin');

				if (dom.getAttrib(n, 'border'))
					this.updateStyle('border');
			}
		}

		// Setup browse button
		document.getElementById('srcbrowsercontainer').innerHTML = getBrowserHTML('srcbrowser','src','image','theme_advanced_image');
		if (isVisible('srcbrowser'))
			document.getElementById('src').style.width = '260px';

		// Setup browse button
		document.getElementById('onmouseoversrccontainer').innerHTML = getBrowserHTML('overbrowser','onmouseoversrc','image','theme_advanced_image');
		if (isVisible('overbrowser'))
			document.getElementById('onmouseoversrc').style.width = '260px';

		// Setup browse button
		document.getElementById('onmouseoutsrccontainer').innerHTML = getBrowserHTML('outbrowser','onmouseoutsrc','image','theme_advanced_image');
		if (isVisible('outbrowser'))
			document.getElementById('onmouseoutsrc').style.width = '260px';

		// If option enabled default contrain proportions to checked
		if (ed.getParam("advimage_constrain_proportions", true))
			f.constrain.checked = true;

		// Check swap image if valid data
		if (nl.onmouseoversrc.value || nl.onmouseoutsrc.value)
			this.setSwapImage(true);
		else
			this.setSwapImage(false);

		this.changeAppearance();
		this.showPreviewImage(nl.src.value, 1);
	},

	insert : function(file, title) {
		var ed = tinyMCEPopup.editor, t = this, f = document.forms[0];

		if (f.src.value === '') {
			if (ed.selection.getNode().nodeName == 'IMG') {
				ed.dom.remove(ed.selection.getNode());
				ed.execCommand('mceRepaint');
			}

			tinyMCEPopup.close();
			return;
		}

		if (tinyMCEPopup.getParam("accessibility_warnings", 1)) {
			if (!f.alt.value) {
				tinyMCEPopup.confirm(tinyMCEPopup.getLang('advimage_dlg.missing_alt'), function(s) {
					if (s)
						t.insertAndClose();
				});

				return;
			}
		}

		t.insertAndClose();
	},

	insertAndClose : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], nl = f.elements, v, args = {}, el;

		tinyMCEPopup.restoreSelection();

		// Fixes crash in Safari
		if (tinymce.isWebKit)
			ed.getWin().focus();

		if (!ed.settings.inline_styles) {
			args = {
				topmargin : nl.topmargin.value,
				bottommargin : nl.bottommargin.value,
				leftmargin : nl.leftmargin.value,
				rightmargin : nl.rightmargin.value,
				border : nl.border.value,
				align : getSelectValue(f, 'align')
			};
		} else {
			// Remove deprecated values
			args = {
				topmargin : '',
				bottommargin : '',
				leftmargin : '',
				rightmargin : '',
				border : '',
				align : ''
			};
		}
        for(i=0; i<document.forms[0].elements.length; i++) {
            //alert(document.forms[0].elements[i].name+":"+document.forms[0].elements[i].name+":"+document.forms[0].elements[i].value);
        }
        //alert(document.forms[0].getElementById('longdesc'));
        //alert('longdesc');
        //alert(nl.longdesc.value);
		tinymce.extend(args, {
			src : nl.src.value,
			width : nl.width.value,
			height : nl.height.value,
			alt : nl.alt.value,
			title : nl.title.value,
			//'class' : getSelectValue(f, 'class_list'),
			'class' : 'embedLight',
			style : nl.style.value,
			id : nl.id.value,
			dir : nl.dir.value,
			lang : nl.lang.value,
			usemap : nl.usemap.value,
			longdesc : nl.longdesc.value
		});

		args.onmouseover = args.onmouseout = '';

		if (f.onmousemovecheck.checked) {
			if (nl.onmouseoversrc.value)
				args.onmouseover = "this.src='" + nl.onmouseoversrc.value + "';";

			if (nl.onmouseoutsrc.value)
				args.onmouseout = "this.src='" + nl.onmouseoutsrc.value + "';";
		}

		el = ed.selection.getNode();

		if (el && el.nodeName == 'IMG') {
			ed.dom.setAttribs(el, args);
		} else {
			ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
			ed.dom.setAttribs('__mce_tmp', args);
			ed.dom.setAttrib('__mce_tmp', 'id', '');
			ed.undoManager.add();
		}

		tinyMCEPopup.close();
	},

	getAttrib : function(e, at) {
		var ed = tinyMCEPopup.editor, dom = ed.dom, v, v2;
		if (ed.settings.inline_styles) {
			switch (at) {
				case 'align':
					if (v = dom.getStyle(e, 'float'))
						return v;

					if (v = dom.getStyle(e, 'vertical-align'))
						return v;

					break;

				case 'topmargin':
					v = dom.getStyle(e, 'margin-top')

					if (v)
						return parseInt(v.replace(/[^0-9]/g, ''));

					break;

				case 'bottommargin':
                    v = dom.getStyle(e, 'margin-bottom')

                    if (v)
                        return parseInt(v.replace(/[^0-9]/g, ''));

                    break;
                
                case 'leftmargin':
                    v = dom.getStyle(e, 'margin-left')

                    if (v)
                        return parseInt(v.replace(/[^0-9]/g, ''));

                    break;

                case 'rightmargin':
                    v = dom.getStyle(e, 'margin-right')

                    if (v)
                        return parseInt(v.replace(/[^0-9]/g, ''));

                    break;
                    
				case 'border':
					v = 0;

					tinymce.each(['top', 'right', 'bottom', 'left'], function(sv) {
						sv = dom.getStyle(e, 'border-' + sv + '-width');

						// False or not the same as prev
						if (!sv || (sv != v && v !== 0)) {
							v = 0;
							return false;
						}

						if (sv)
							v = sv;
					});

					if (v)
						return parseInt(v.replace(/[^0-9]/g, ''));

					break;
			}
		}

		if (v = dom.getAttrib(e, at))
			return v;

		return '';
	},

	setSwapImage : function(st) {
		var f = document.forms[0];

		f.onmousemovecheck.checked = st;
		setBrowserDisabled('overbrowser', !st);
		setBrowserDisabled('outbrowser', !st);

		if (f.over_list)
			f.over_list.disabled = !st;

		if (f.out_list)
			f.out_list.disabled = !st;

		f.onmouseoversrc.disabled = !st;
		f.onmouseoutsrc.disabled  = !st;
	},

	fillClassList : function(id) {
		var dom = tinyMCEPopup.dom, lst = dom.get(id), v, cl;

		if (v = tinyMCEPopup.getParam('theme_advanced_styles')) {
			cl = [];

			tinymce.each(v.split(';'), function(v) {
				var p = v.split('=');
				cl.push({'title' : p[0], 'class' : p[1]});
			});
		} else
			cl = tinyMCEPopup.editor.dom.getClasses();

		if (cl.length > 0) {
			lst.options.length = 0;
			lst.options[lst.options.length] = new Option(tinyMCEPopup.getLang('not_set'), '');

			tinymce.each(cl, function(o) {
				lst.options[lst.options.length] = new Option(o.title || o['class'], o['class']);
			});
		} else
			dom.remove(dom.getParent(id, 'tr'));
	},

	fillFileList : function(id, l) {
		var dom = tinyMCEPopup.dom, lst = dom.get(id), v, cl;

		l = window[l];
		lst.options.length = 0;

		if (l && l.length > 0) {
			lst.options[lst.options.length] = new Option('', '');

			tinymce.each(l, function(o) {
				lst.options[lst.options.length] = new Option(o[0], o[1]);
			});
		} else
			dom.remove(dom.getParent(id, 'tr'));
	},

	resetImageData : function() {
		var f = document.forms[0];

		f.elements.width.value = f.elements.height.value = '';
	},

	updateImageData : function(img, st) {
		var f = document.forms[0];

		if (!st) {
			f.elements.width.value = img.width;
			f.elements.height.value = img.height;
		}

		this.preloadImg = img;
	},

	changeAppearance : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], img = document.getElementById('alignSampleImg');

		if (img) {
			if (ed.getParam('inline_styles')) {
				ed.dom.setAttrib(img, 'style', f.style.value);
			} else {
				img.align = f.align.value;
				img.border = f.border.value;
				img.topmargin = f.topmargin.value;
				img.bottommargin = f.bottommargin.value;
				img.leftmargin = f.leftmargin.value;
                img.rightmargin = f.rightmargin.value;
			}
		}
	},

	changeHeight : function() {
		var f = document.forms[0], tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "")
			return;

		tp = (parseInt(f.width.value) / parseInt(t.preloadImg.width)) * t.preloadImg.height;
		f.height.value = tp.toFixed(0);
	},

	changeWidth : function() {
		var f = document.forms[0], tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "")
			return;

		tp = (parseInt(f.height.value) / parseInt(t.preloadImg.height)) * t.preloadImg.width;
		f.width.value = tp.toFixed(0);
	},

	updateStyle : function(ty) {
		var dom = tinyMCEPopup.dom, st, v, f = document.forms[0], img = dom.create('img', {style : dom.get('style').value});
		if (tinyMCEPopup.editor.settings.inline_styles) {

			// Handle width
			if (ty == 'width') {
				dom.setStyle(img, 'width', '');
				f.width.value='';
				f.height.value='';
				//dom.setStyle(img, 'vertical-align', '');

				v = getSelectValue(f, 'width_pct');
				if (v) {
					img.style.width=v;
					document.getElementById('img_width_manual').style.display="none";
				}
				else{
					document.getElementById('img_width_manual').style.display="block";
				}
			}

			// Handle align
			if (ty == 'align') {
				dom.setStyle(img, 'float', '');
				dom.setStyle(img, 'vertical-align', '');

				v = getSelectValue(f, 'align');
				if (v) {
					if (v == 'left' || v == 'right') {
					    if(v == 'left') {
					        document.getElementById('topmargin').value = '10';
					        document.getElementById('bottommargin').value = '10';
					        document.getElementById('leftmargin').value = '0';
					        document.getElementById('rightmargin').value = '10';
					        dom.setStyle(img, 'margin', '10px 10px 10px 0px');
					    } else {
					        document.getElementById('topmargin').value = '10';
                            document.getElementById('bottommargin').value = '10';
                            document.getElementById('leftmargin').value = '10';
                            document.getElementById('rightmargin').value = '0';
					        dom.setStyle(img, 'margin', '10px 0px 10px 10px');
					    }
						dom.setStyle(img, 'float', v);
					} else {
						img.style.verticalAlign = v;
					}
				}
			}

			// Handle border
			if (ty == 'border') {
				dom.setStyle(img, 'border', '');

				v = f.border.value;
				if (v || v == '0') {
					if (v == '0')
						img.style.border = '0';
					else
						img.style.border = v + 'px solid black';
				}
			}

			// Handle topmargin
			if (ty == 'topmargin') {
				dom.setStyle(img, 'marginTop', '');

				v = f.topmargin.value;
				if (v) {
					img.style.marginTop = v + 'px';
				}
			}
			
			// Handle bottommargin
            if (ty == 'bottommargin') {
                dom.setStyle(img, 'marginBottom', '');

                v = f.bottommargin.value;
                if (v) {
                    img.style.marginBottom = v + 'px';
                }
            }
            
            // Handle leftmargin
            if (ty == 'leftmargin') {
                dom.setStyle(img, 'marginLeft', '');

                v = f.leftmargin.value;
                if (v) {
                    img.style.marginLeft = v + 'px';
                }
            }
            
            // Handle rightmargin
            if (ty == 'rightmargin') {
                dom.setStyle(img, 'marginRight', '');

                v = f.rightmargin.value;
                if (v) {
                    img.style.marginRight = v + 'px';
                }
            }

			// Merge
			dom.get('style').value = dom.serializeStyle(dom.parseStyle(img.style.cssText), 'img');
		}
	},

	changeMouseMove : function() {
	},

	showPreviewImage : function(u, st) {
		if (!u) {
			tinyMCEPopup.dom.setHTML('prev', '');
			return;
		}

		if (!st && tinyMCEPopup.getParam("advimage_update_dimensions_onchange", true))
			this.resetImageData();

		u = tinyMCEPopup.editor.documentBaseURI.toAbsolute(u);

		if (!st)
			tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this);" onerror="ImageDialog.resetImageData();" />');
		else
			tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this, 1);" />');
	}
};

ImageDialog.preInit();
tinyMCEPopup.onInit.add(ImageDialog.init, ImageDialog);
