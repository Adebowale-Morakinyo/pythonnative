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

    # web_view = pn.WebView(context)
    # web_view.load_url("https://www.djangoproject.com/")
    # layout.add_view(web_view)
    #
    # for i in range(100):
    #     button = pn.Button(context, "Click me")
    #     layout.add_view(button)

    return layout.native_instance
