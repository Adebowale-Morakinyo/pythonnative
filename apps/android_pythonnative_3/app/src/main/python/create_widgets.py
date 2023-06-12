from java import cast, jclass

def create_widgets(context):
    # Java Classes
    LinearLayout = jclass('android.widget.LinearLayout')
    Button = jclass('android.widget.Button')
    TextView = jclass('android.widget.TextView')
    EditText = jclass('android.widget.EditText')
    CheckBox = jclass('android.widget.CheckBox')
    RadioButton = jclass('android.widget.RadioButton')
    ImageView = jclass('android.widget.ImageView')
    ProgressBar = jclass('android.widget.ProgressBar')
    Switch = jclass('android.widget.Switch')
    ToggleButton = jclass('android.widget.ToggleButton')
    SeekBar = jclass('android.widget.SeekBar')

    # Create LinearLayout
    layout = LinearLayout(context)
    layout_params = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                                             LinearLayout.LayoutParams.WRAP_CONTENT)
    layout.setLayoutParams(layout_params)
    layout.setOrientation(LinearLayout.VERTICAL)

    # Create Button
    button = Button(context)
    button.setText('Button created in Python')
    layout.addView(button)

    # Create TextView
    textView = TextView(context)
    textView.setText('TextView created in Python')
    layout.addView(textView)

    # Create EditText
    editText = EditText(context)
    editText.setHint('EditText created in Python')
    layout.addView(editText)

    # Create CheckBox
    checkBox = CheckBox(context)
    checkBox.setText('CheckBox created in Python')
    layout.addView(checkBox)

    # Create RadioButton
    radioButton = RadioButton(context)
    radioButton.setText('RadioButton created in Python')
    layout.addView(radioButton)

    # Create ImageView
    imageView = ImageView(context)
    layout.addView(imageView)

    # Create ProgressBar
    progressBar = ProgressBar(context)
    layout.addView(progressBar)

    # Create Switch
    switch = Switch(context)
    switch.setText('Switch created in Python')
    layout.addView(switch)

    # Create ToggleButton
    toggleButton = ToggleButton(context)
    toggleButton.setTextOn('On')
    toggleButton.setTextOff('Off')
    layout.addView(toggleButton)

    # Create SeekBar
    seekBar = SeekBar(context)
    layout.addView(seekBar)

    # Return layout
    return layout
