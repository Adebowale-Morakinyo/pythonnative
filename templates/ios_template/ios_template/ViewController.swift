//
//  ViewController.swift
//  ios_template
//
//  Created by Owen Carey on 6/19/23.
//

import UIKit
import PythonKit

class ViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Attempt Python bootstrap of app.main_page.bootstrap(self)
        let sys = Python.import("sys")
        if let resourcePath = Bundle.main.resourcePath {
            sys.path.append(resourcePath)
            sys.path.append("\(resourcePath)/app")
        }
        do {
            let app = try Python.attemptImport("app.main_page")
            let bootstrap = app.bootstrap
            _ = bootstrap(self)
            return
        } catch {
            print("Python bootstrap failed: \(error)")
        }

        // Fallback UI if Python import/bootstrap fails
        let label = UILabel(frame: view.bounds)
        label.text = "Hello from PythonNative (iOS template)"
        label.textAlignment = .center
        label.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(label)
    }


}

