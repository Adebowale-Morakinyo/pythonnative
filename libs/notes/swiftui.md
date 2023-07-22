This is from the Apple UIKit docs
(https://developer.apple.com/documentation/uikit):

"UIKit works seamlessly with the SwiftUI framework, so you can implement parts of
your UIKit app in SwiftUI or mix interface elements between the two frameworks.
For example, you can place UIKit views and view controllers inside SwiftUI
views, and vice versa."

Could you show me how to do this?

---

Sure, I can help with that. You can use UIKit views in SwiftUI by conforming to
the `UIViewRepresentable` protocol, and you can use SwiftUI views in UIKit by
wrapping them in a `UIHostingController`. Here's an example of each.

## UIKit views in SwiftUI

First, let's show how to use a UIKit view in a SwiftUI view. We'll use a
`UISlider` as an example:

```swift
import SwiftUI
import UIKit

struct UIKitSlider: UIViewRepresentable {
    @Binding var value: Float

    func makeUIView(context: Context) -> UISlider {
        let slider = UISlider(frame: .zero)
        slider.value = value
        slider.addTarget(context.coordinator, action: #selector(Coordinator.valueChanged(_:)), for: .valueChanged)
        return slider
    }

    func updateUIView(_ uiView: UISlider, context: Context) {
        uiView.value = value
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(value: $value)
    }

    class Coordinator: NSObject {
        var value: Binding<Float>

        init(value: Binding<Float>) {
            self.value = value
        }

        @objc func valueChanged(_ sender: UISlider) {
            self.value.wrappedValue = sender.value
        }
    }
}
```

You can then use `UIKitSlider` in your SwiftUI views like this:

```swift
struct ContentView: View {
    @State private var sliderValue: Float = 0.5

    var body: some View {
        VStack {
            Text("Slider Value: \(sliderValue)")
            UIKitSlider(value: $sliderValue)
        }
    }
}
```

## SwiftUI views in UIKit

You can also embed SwiftUI views in your UIKit code by using a
UIHostingController. Here's an example of how to do that:

```swift
import SwiftUI
import UIKit

struct SwiftUIView: View {
    var body: some View {
        Text("Hello, SwiftUI!")
            .padding()
            .background(Color.green)
            .foregroundColor(.white)
            .cornerRadius(10)
    }
}

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let hostingController = UIHostingController(rootView: SwiftUIView())
        addChild(hostingController)
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(hostingController.view)

        NSLayoutConstraint.activate([
            hostingController.view.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            hostingController.view.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
    }
}
```

In this example, `SwiftUIView` is embedded in a `ViewController`. It will
display a text "Hello, SwiftUI!" with a green background in the center of the
screen.

---

Could you show me how to place a UIViewController (instead of just a UIView)
inside SwiftUI views?

---

## UIKit UIViewControllers in SwiftUI

Yes, absolutely! In order to use a `UIViewController` in a SwiftUI view, you
need to use the `UIViewControllerRepresentable` protocol. Here's an example of
how to use a `UIImagePickerController` (which is a subclass of
`UIViewController`) inside a SwiftUI view:

```swift
import SwiftUI
import UIKit

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.presentationMode) private var presentationMode

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        var parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let uiImage = info[.originalImage] as? UIImage {
                parent.selectedImage = uiImage
            }

            parent.presentationMode.wrappedValue.dismiss()
        }
    }

    func makeUIViewController(context: UIViewControllerRepresentableContext<ImagePicker>) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: UIViewControllerRepresentableContext<ImagePicker>) {
        // update function implementation
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
}
```

You can then use `ImagePicker` in your SwiftUI views like this:

```swift
struct ContentView: View {
    @State private var isShowingImagePicker = false
    @State private var selectedImage: UIImage?

    var body: some View {
        VStack {
            Button(action: {
                isShowingImagePicker = true
            }) {
                Text("Open Image Picker")
            }

            selectedImage.map { Image(uiImage: $0).resizable().scaledToFit() }
        }
        .sheet(isPresented: $isShowingImagePicker) {
            ImagePicker(selectedImage: $selectedImage)
        }
    }
}
```

In this example, when you press the "Open Image Picker" button, it opens up an
image picker. Once an image is selected, it is displayed on the screen.

---

Does SwiftUI render to UIKit on mobile and AppKit on desktop?

---

In essence, yes. SwiftUI operates at a higher level of abstraction than UIKit or
AppKit. When you define interfaces in SwiftUI, you describe them in a
platform-agnostic way, but when those interfaces are rendered on a particular
platform, SwiftUI uses the native rendering engine of that platform.

On iOS and iPadOS, SwiftUI uses UIKit (more specifically, underlying
technologies like Core Animation and Core Graphics) for rendering. On macOS,
SwiftUI uses AppKit. Similarly, on watchOS, it uses WatchKit, and on tvOS, it
uses TVUIKit.

However, it's important to note that SwiftUI doesn't directly convert your
SwiftUI views into UIKit or AppKit components. Instead, SwiftUI works directly
with the underlying rendering and layout engines to create UIs that match the
capabilities and conventions of each platform.

This means, for instance, that a SwiftUI `Button` does not become a `UIButton`
on iOS or a `NSButton` on macOS. It remains a SwiftUI `Button`, but it is drawn
and behaves appropriately for the platform it's running on, thanks to the
rendering done by SwiftUI using the native technologies.
