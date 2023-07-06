import pythonnative as pn


def main(context):
    layout = pn.LinearLayout(context)

    # label = pn.Label(context, "This is a PythonNative label")
    # layout.add_view(label)
    #
    # switch = pn.Switch(context)
    # layout.add_view(switch)
    #
    # text_field = pn.TextField(context)
    # layout.add_view(text_field)
    #
    # text_view = pn.TextView(context)
    # layout.add_view(text_view)

    activity_indicator_view = pn.ActivityIndicatorView(context)
    activity_indicator_view.start_animating()
    layout.add_view(activity_indicator_view)

    material_activity_indicator_view = pn.MaterialActivityIndicatorView(context)
    material_activity_indicator_view.start_animating()
    layout.add_view(material_activity_indicator_view)

    progress_view = pn.ProgressView(context)
    progress_view.set_progress(0.5)
    layout.add_view(progress_view)

    material_progress_view = pn.MaterialProgressView(context)
    material_progress_view.set_progress(0.5)
    layout.add_view(material_progress_view)

    material_button = pn.MaterialButton(context, "MaterialButton")
    layout.add_view(material_button)

    search_bar = pn.SearchBar(context)
    layout.add_view(search_bar)

    image_view = pn.ImageView(context)
    layout.add_view(image_view)

    picker_view = pn.PickerView(context)
    layout.add_view(picker_view)

    # date_picker = pn.DatePicker(context)
    # layout.add_view(date_picker)

    # time_picker = pn.TimePicker(context)
    # layout.add_view(time_picker)

    # TODO: fix
    # material_time_picker = pn.MaterialTimePicker(context)
    # layout.add_view(material_time_picker)

    # TODO: fix
    # material_date_picker = pn.MaterialDatePicker(context)
    # layout.add_view(material_date_picker)

    # TODO: fix
    # material_switch = pn.MaterialSwitch(context)
    # layout.add_view(material_switch)

    # TODO: fix
    # material_search_bar = pn.MaterialSearchBar(context)
    # layout.add_view(material_search_bar)

    # web_view = pn.WebView(context)
    # web_view.load_url("https://www.djangoproject.com/")
    # layout.add_view(web_view)
    #
    # for i in range(100):
    #     button = pn.Button(context, "Click me")
    #     layout.add_view(button)

    return layout.native_instance
