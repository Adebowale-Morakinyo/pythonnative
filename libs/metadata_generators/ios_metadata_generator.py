import clang.cindex
import json

clang.cindex.Config.set_library_path("/usr/local/Cellar/llvm/16.0.4/lib/")
index = clang.cindex.Index.create()


def extract(cursor):
    print(f"{cursor.kind}: {cursor.spelling}")
    data = {"Name": cursor.spelling}
    if cursor.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
        data["Type"] = "Interface"
    elif cursor.kind in [
        clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL,
        clang.cindex.CursorKind.OBJC_CLASS_METHOD_DECL,
    ]:
        data["Type"] = "Method"
    elif cursor.kind == clang.cindex.CursorKind.OBJC_PROPERTY_DECL:
        data["Type"] = "Property"
    else:
        data["Type"] = "Other"  # Add this line
    try:
        children = [extract(c) for c in cursor.get_children()]
    except ValueError as e:
        print(f"Encountered error with cursor {cursor.spelling}: {e}")
        children = []
    children = [c for c in children if c is not None]
    if children:
        data["Children"] = children
    return data


def main():
    args = [
        "-x", "objective-c",
        "-arch", "arm64",
        "-fno-objc-arc",
        # "-fmodules",
        # "-fmodule-maps",
        "-ferror-limit=0",
        "-isysroot",
        "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk",
        "-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/usr/include",
        "-I/usr/local/include",
        "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/14.0.3/include",
        "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include",
        "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include",
        "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks"
    ]
    tu = index.parse(
        "/Applications/Xcode.app/Contents/Developer/Platforms/"
        "iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/"
        "Library/Frameworks/UIKit.framework/Headers/UIKit.h",
        args
    )
    print(f"Translation unit: {tu.spelling}")
    for diag in tu.diagnostics:
        print(diag)
    metadata = extract(tu.cursor)
    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
