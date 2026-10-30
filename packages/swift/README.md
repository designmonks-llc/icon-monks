# Icon Monks for iOS, macOS, tvOS and watchOS

[![Swift Package Manager](https://img.shields.io/badge/Swift_Package_Manager-compatible-orange)](https://github.com/designmonks-llc/icon-monks)
[![release](https://img.shields.io/github/v/release/designmonks-llc/icon-monks)](https://github.com/designmonks-llc/icon-monks/releases)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

6,054 icons for SwiftUI and UIKit in six weights, including duotone, as a Swift package. Vector assets that stay sharp at any size and take the tint color, just like SF Symbols. A product of [Design Monks](https://www.designmonks.co). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

## Install

In Xcode choose **File > Add Package Dependencies** and enter `https://github.com/designmonks-llc/icon-monks`, or add it
to `Package.swift`:

```swift
.package(url: "https://github.com/designmonks-llc/icon-monks", from: "0.4.2")
```

Requires iOS 14, macOS 11, tvOS 14 or watchOS 7.

## SwiftUI

```swift
import IconMonks

Image(iconMonks: .house)
    .resizable()
    .frame(width: 24, height: 24)
    .foregroundStyle(.purple)              // iOS 15+; use .foregroundColor(.purple) on iOS 14

Image(iconMonks: .heart, weight: .fill)
```

Icon names are the same in every weight, so changing the look is one parameter, never a rename.

### Dynamic Type

`IconMonkImage` scales with the user's text size, so icons grow alongside your labels at accessibility sizes:

```swift
IconMonkImage(.house)                                   // 24 pt at the default text size, scales like .body
IconMonkImage(.bell, weight: .bold, size: 20, relativeTo: .headline)
    .foregroundStyle(.purple)

Label { Text("Home") } icon: { IconMonkImage(.house, size: 17) }
```

## UIKit and AppKit

```swift
let tabIcon = IconMonk.gear.uiImage(.bold)    // UIKit
let menuIcon = IconMonk.gear.nsImage(.light)  // AppKit
```

Weights: `.thin`, `.light`, `.regular`, `.bold`, `.fill` and `.duotone`. Names on the website are kebab-case; in Swift
they are camelCase, so `arrow-right` is `IconMonk.arrowRight`. `IconMonk.allCases` lists every icon.

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://www.designmonks.co).
