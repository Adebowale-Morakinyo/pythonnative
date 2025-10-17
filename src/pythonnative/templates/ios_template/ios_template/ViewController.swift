//
//  ViewController.swift
//  ios_template
//
//  Created by Owen Carey on 6/19/23.
//

import UIKit
// PythonKit isn't available on iOS by default; guard its use so the
// template builds out of the box and falls back to a native label.
#if canImport(PythonKit)
import PythonKit
#endif
#if canImport(Python)
import Python
#endif

class ViewController: UIViewController {
    // Ensure Python.framework is configured only once per process
    private static var hasInitializedPython: Bool = false
    // Optional keys for dynamic page navigation
    @objc dynamic var requestedPagePath: String? = nil
    @objc dynamic var requestedPageArgsJSON: String? = nil
    private var pythonReady: Bool = false

    override func viewDidLoad() {
        super.viewDidLoad()
        // Ensure a visible background when created programmatically (storyboards set this automatically)
        view.backgroundColor = .systemBackground
        NSLog("[PN][ViewController] viewDidLoad")
        if let bundleId = Bundle.main.bundleIdentifier {
            NSLog("[PN] Bundle Identifier: \(bundleId)")
        }
        NSLog("[PN] Bundle Path: \(Bundle.main.bundlePath)")
        NSLog("[PN] Resource Path: \(Bundle.main.resourcePath ?? "nil")")
        // Configure embedded Python if available in bundle
        if let resourcePath = Bundle.main.resourcePath {
            let pyStd = "\(resourcePath)/python-stdlib"
            let pyDyn = "\(resourcePath)/python-stdlib/lib-dynload"
            var pyPath = "\(pyStd):\(pyDyn):\(resourcePath):\(resourcePath)/app"
            let platSite = "\(resourcePath)/platform-site"
            if FileManager.default.fileExists(atPath: platSite) {
                pyPath += ":\(platSite)"
            }
            setenv("PYTHONHOME", pyStd, 1)
            setenv("PYTHONPATH", pyPath, 1)
            NSLog("[PN] Set PYTHONHOME=\(pyStd)")
            NSLog("[PN] Set PYTHONPATH=\(pyPath)")
        }
        #if canImport(PythonKit)
        // Ensure PythonKit knows where to load the Python library from when using an embedded framework.
        if let bundlePath = Bundle.main.bundlePath as String? {
            let frameworkLib = "\(bundlePath)/Frameworks/Python.framework/Python"
            setenv("PYTHON_LIBRARY", frameworkLib, 1)
            if FileManager.default.fileExists(atPath: frameworkLib) {
                if !ViewController.hasInitializedPython {
                    NSLog("[PN] Using embedded Python lib at: \(frameworkLib)")
                    PythonLibrary.useLibrary(at: frameworkLib)
                    ViewController.hasInitializedPython = true
                } else {
                    NSLog("[PN] Python library already initialized; skipping useLibrary")
                }
                pythonReady = true
            } else {
                NSLog("[PN] Embedded Python library not found at: \(frameworkLib)")
            }
        }
        NSLog("[PN] PythonKit available; attempting Python bootstrap")
        let sys = Python.import("sys")
        NSLog("[PN] Python version: \(sys.version)")
        NSLog("[PN] Initial sys.path: \(sys.path)")
        if let resourcePath = Bundle.main.resourcePath {
            sys.path.append(resourcePath)
            sys.path.append("\(resourcePath)/app")
            NSLog("[PN] Updated sys.path: \(sys.path)")
            // List bundled resources to verify Python files are present
            let fm = FileManager.default
            let appDir = "\(resourcePath)/app"
            if let entries = try? fm.contentsOfDirectory(atPath: appDir) {
                NSLog("[PN] Contents of /app in bundle: \(entries)")
            } else {
                NSLog("[PN] Could not list contents of \(appDir).")
            }
        }
        // Determine which Python page to load
        let pagePath: String = requestedPagePath ?? "app.main_page.MainPage"
        do {
            let moduleName = String(pagePath.split(separator: ".").dropLast().joined(separator: "."))
            let className = String(pagePath.split(separator: ".").last ?? "MainPage")
            let pyModule = try Python.attemptImport(moduleName)
            // Resolve class by name via builtins.getattr to avoid subscripting issues
            let builtins = Python.import("builtins")
            let getattrFn = builtins.getattr
            let pageClass = try getattrFn.throwing.dynamicallyCall(withArguments: [pyModule, className])
            // Pass native pointer so Python Page can wrap via rubicon.objc
            let ptr = Unmanaged.passUnretained(self).toOpaque()
            let addr = UInt(bitPattern: ptr)
            let page = try pageClass.throwing.dynamicallyCall(withArguments: [addr])
            // If args provided, pass into Page via set_args(dict)
            if let jsonStr = requestedPageArgsJSON {
                let json = Python.import("json")
                do {
                    let args = try json.loads.throwing.dynamicallyCall(withArguments: [jsonStr])
                    _ = try page.set_args.throwing.dynamicallyCall(withArguments: [args])
                } catch {
                    NSLog("[PN] Failed to decode requestedPageArgsJSON: \(error)")
                }
            }
            // Call on_create immediately so Python can insert its root view
            _ = try page.on_create.throwing.dynamicallyCall(withArguments: [])
            return
        } catch {
            NSLog("[PN] Python bootstrap failed: \(error)")
        }
        #endif

        // Fallback UI if Python import/bootstrap fails
        NSLog("[PN] Python unavailable or bootstrap failed; showing fallback UILabel")
        let label = UILabel(frame: view.bounds)
        label.text = "Hello from PythonNative (iOS template)"
        label.textAlignment = .center
        label.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(label)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_start"])
            } catch {}
        }
        #endif
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_resume"])
            } catch {}
        }
        #endif
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_pause"])
            } catch {}
        }
        #endif
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_stop"])
            } catch {}
        }
        #endif
    }

    override func encodeRestorableState(with coder: NSCoder) {
        super.encodeRestorableState(with: coder)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_save_instance_state"])
            } catch {}
        }
        #endif
    }

    override func decodeRestorableState(with coder: NSCoder) {
        super.decodeRestorableState(with: coder)
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_restore_instance_state"])
            } catch {}
        }
        #endif
    }

    deinit {
        #if canImport(PythonKit)
        if pythonReady {
            let ptr = UInt(bitPattern: Unmanaged.passUnretained(self).toOpaque())
            do {
                let pn = try Python.attemptImport("pythonnative.page")
                _ = try pn.forward_lifecycle.throwing.dynamicallyCall(withArguments: [ptr, "on_destroy"])
            } catch {}
        }
        #endif
    }


}

