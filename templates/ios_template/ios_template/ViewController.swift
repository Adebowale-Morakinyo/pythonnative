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
        // Minimal PythonKit bootstrap: print Python version and attempt to import Rubicon.
        let sys = Python.import("sys")
        print("Python Version: \(sys.version_info.major).\(sys.version_info.minor)")
        print("Python Path: \(sys.path)")

        // Try to import Rubicon-ObjC if available. Safe no-op if not present.
        do {
            let rubiconObjC = try Python.attemptImport("rubicon.objc")
            let ObjCClass = rubiconObjC.ObjCClass
            print("Rubicon available: \(ObjCClass)")
        } catch {
            print("Rubicon not available; continuing without it.")
        }
    }


}

