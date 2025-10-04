from java import jclass

# Layouts
AbsoluteLayout = jclass("android.widget.AbsoluteLayout")
CoordinatorLayout = jclass("androidx.coordinatorlayout.widget.CoordinatorLayout")
ConstraintLayout = jclass("androidx.constraintlayout.widget.ConstraintLayout")
DrawerLayout = jclass("androidx.drawerlayout.widget.DrawerLayout")
FrameLayout = jclass("android.widget.FrameLayout")
GridLayout = jclass("android.widget.GridLayout")
HorizontalScrollView = jclass("android.widget.HorizontalScrollView")
LinearLayout = jclass("android.widget.LinearLayout")
RelativeLayout = jclass("android.widget.RelativeLayout")
RecyclerView = jclass("androidx.recyclerview.widget.RecyclerView")
ScrollView = jclass("android.widget.ScrollView")
TableLayout = jclass("android.widget.TableLayout")
TableRow = jclass("android.widget.TableRow")

# Widgets
AutoCompleteTextView = jclass("android.widget.AutoCompleteTextView")
Button = jclass("android.widget.Button")
CheckBox = jclass("android.widget.CheckBox")
DatePicker = jclass("android.widget.DatePicker")
EditText = jclass("android.widget.EditText")
ImageView = jclass("android.widget.ImageView")
ProgressBar = jclass("android.widget.ProgressBar")
RadioButton = jclass("android.widget.RadioButton")
RatingBar = jclass("android.widget.RatingBar")
SeekBar = jclass("android.widget.SeekBar")
Spinner = jclass("android.widget.Spinner")
Switch = jclass("android.widget.Switch")
TextView = jclass("android.widget.TextView")
TimePicker = jclass("android.widget.TimePicker")
ToggleButton = jclass("android.widget.ToggleButton")
ViewFlipper = jclass("android.widget.ViewFlipper")
ViewSwitcher = jclass("android.widget.ViewSwitcher")
WebView = jclass("android.webkit.WebView")

# Material Components
BottomNavigationView = jclass(
    "com.google.android.material.bottomnavigation.BottomNavigationView"
)
BottomSheetDialogFragment = jclass(
    "com.google.android.material.bottomsheet.BottomSheetDialogFragment"
)
Chip = jclass("com.google.android.material.chip.Chip")
FloatingActionButton = jclass(
    "com.google.android.material.floatingactionbutton.FloatingActionButton"
)
MaterialCardView = jclass("com.google.android.material.card.MaterialCardView")
NavigationView = jclass("com.google.android.material.navigation.NavigationView")
Snackbar = jclass("com.google.android.material.snackbar.Snackbar")
TextInputLayout = jclass("com.google.android.material.textfield.TextInputLayout")
