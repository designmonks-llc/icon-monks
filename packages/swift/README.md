# Icon Monks for iOS, macOS, tvOS and watchOS

In Xcode choose File > Add Package Dependencies and enter `https://github.com/designmonks/icon-monks`, or in
`Package.swift`:

```swift
.package(url: "https://github.com/designmonks/icon-monks", from: "0.2.0")
```

```swift
import IconMonks

Image(iconMonks: .house)
    .resizable()
    .frame(width: 24, height: 24)
    .foregroundStyle(.purple)

Image(iconMonks: .heart, weight: .fill)
let tabIcon = IconMonk.gear.uiImage(.bold)   // UIKit
```

Icons ship as vector SVG assets (preserved vector data, template rendering), so they stay sharp at any size and take
the tint colour like SF Symbols. All six weights, including duotone, are available.
