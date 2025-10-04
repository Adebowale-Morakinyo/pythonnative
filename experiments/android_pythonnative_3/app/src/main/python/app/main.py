import pythonnative as pn


def on_create(context):
    stack_view = pn.StackView(context)

    # label = pn.Label(context, "This is a PythonNative label")
    # stack_view.add_view(label)
    #
    # switch = pn.Switch(context)
    # stack_view.add_view(switch)
    #
    # text_field = pn.TextField(context)
    # stack_view.add_view(text_field)
    #
    # text_view = pn.TextView(context)
    # stack_view.add_view(text_view)

    activity_indicator_view = pn.ActivityIndicatorView(context)
    activity_indicator_view.start_animating()
    stack_view.add_view(activity_indicator_view)

    material_activity_indicator_view = pn.MaterialActivityIndicatorView(context)
    material_activity_indicator_view.start_animating()
    stack_view.add_view(material_activity_indicator_view)

    progress_view = pn.ProgressView(context)
    progress_view.set_progress(0.5)
    stack_view.add_view(progress_view)

    material_progress_view = pn.MaterialProgressView(context)
    material_progress_view.set_progress(0.5)
    stack_view.add_view(material_progress_view)

    material_button = pn.MaterialButton(context, "MaterialButton")
    stack_view.add_view(material_button)

    search_bar = pn.SearchBar(context)
    stack_view.add_view(search_bar)

    image_view = pn.ImageView(context)
    stack_view.add_view(image_view)

    picker_view = pn.PickerView(context)
    stack_view.add_view(picker_view)

    # date_picker = pn.DatePicker(context)
    # stack_view.add_view(date_picker)

    # time_picker = pn.TimePicker(context)
    # stack_view.add_view(time_picker)

    # TODO: fix
    # material_time_picker = pn.MaterialTimePicker(context)
    # stack_view.add_view(material_time_picker)

    # TODO: fix
    # material_date_picker = pn.MaterialDatePicker(context)
    # stack_view.add_view(material_date_picker)

    # TODO: fix
    # material_switch = pn.MaterialSwitch(context)
    # stack_view.add_view(material_switch)

    # TODO: fix
    # material_search_bar = pn.MaterialSearchBar(context)
    # stack_view.add_view(material_search_bar)

    # web_view = pn.WebView(context)
    # web_view.load_url("https://www.djangoproject.com/")
    # stack_view.add_view(web_view)
    #
    # for i in range(100):
    #     button = pn.Button(context, "Click me")
    #     stack_view.add_view(button)

    return stack_view.native_instance


def on_start():
    print("on_start() called")


def on_resume():
    print("on_resume() called")


def on_pause():
    print("on_pause() called")


def on_stop():
    print("on_stop() called")


def on_destroy():
    print("on_destroy() called")


def on_restart():
    print("on_restart() called")


def on_save_instance_state():
    print("on_save_instance_state() called")


def on_restore_instance_state():
    print("on_restore_instance_state() called")
