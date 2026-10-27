"""Small menu delta from delivered v25; geometry/callbacks stay unchanged."""
def build_menu_v26(file):
    from build_menu_v19 import MenuEditor
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    e=MenuEditor(file)
    e.text(e.find('Menu/CC_Graphics/CC_GraphicsLocal'),
           'Changes are saved and take effect after restarting Cloudcourt.')
    return dict(changed_existing_ids=[i for i,b in before.items() if file.objects[i].get_raw_data()!=b],
                created_ids=sorted(set(file.objects)-set(before)),restart_required=True,
                geometry_unchanged=True)
