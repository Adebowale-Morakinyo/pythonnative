from java import jclass


BottomNavigationView = jclass(
    "com.google.android.material.bottomnavigation.BottomNavigationView"
)
ConstraintLayout = jclass("androidx.constraintlayout.widget.ConstraintLayout")
View = jclass("android.view.View")
ViewGroup = jclass("android.view.ViewGroup")


def create_constraint_layout(context):
    # Create ConstraintLayout
    layout = ConstraintLayout(context)
    layout_params = ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT
    )
    layout.setLayoutParams(layout_params)

    # Create BottomNavigationView
    bottom_nav = BottomNavigationView(context)
    bottom_nav.setId(View.generateViewId()) # Add this line to generate unique id for the view

    # Create Menu for BottomNavigationView
    menu = bottom_nav.getMenu()

    # Add items to the menu
    menu.add(0, 0, 0, "Home")
    menu.add(0, 1, 0, "Search")
    menu.add(0, 2, 0, "Notifications")
    menu.add(0, 3, 0, "Messages")
    menu.add(0, 4, 0, "Profile")

    # Add BottomNavigationView to ConstraintLayout
    nav_layout_params = ConstraintLayout.LayoutParams(
        ConstraintLayout.LayoutParams.MATCH_PARENT,
        ConstraintLayout.LayoutParams.WRAP_CONTENT
    )
    # Set the constraints here
    nav_layout_params.bottomToBottom = ConstraintLayout.LayoutParams.PARENT_ID
    bottom_nav.setLayoutParams(nav_layout_params)
    layout.addView(bottom_nav)

    return layout
