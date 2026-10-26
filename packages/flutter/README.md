# Icon Monks for Flutter

[![pub version](https://img.shields.io/pub/v/icon_monks)](https://pub.dev/packages/icon_monks)
[![pub points](https://img.shields.io/pub/points/icon_monks)](https://pub.dev/packages/icon_monks/score)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

6,054 open source icons for Flutter in five weights: thin, light, regular, bold and fill. Every icon is drawn on
the same 256-unit grid, so they line up with each other and with your text. A product of
[Design Monks](https://monks.company/).

- **One `IconData` per icon and weight**, ready for `Icon`, `IconButton`, `NavigationBar` and anything else that takes an icon.
- **Works on every platform** Flutter supports: Android, iOS, web, macOS, Windows and Linux.
- **Small release builds.** Flutter's icon tree shaking keeps only the glyphs your app uses.
- **No dependencies** beyond Flutter itself.

Browse and search every icon at **[iconmonks.co](https://www.iconmonks.co/)**.

## Install

```sh
flutter pub add icon_monks
```

## Usage

```dart
import 'package:icon_monks/icon_monks.dart';

const Icon(IconMonks.house)                      // regular weight
Icon(IconMonks.bold.heart, color: Colors.red)    // pick a weight
Icon(IconMonks.fill.star, size: 32)
IconButton(icon: Icon(IconMonks.light.gear), onPressed: () {})
```

Icons follow `IconTheme`, so size and color can be set once for a whole subtree:

```dart
IconTheme(
  data: const IconThemeData(size: 20, color: Colors.indigo),
  child: Row(children: [Icon(IconMonks.regular.house), Icon(IconMonks.regular.bell)]),
)
```

## Weights

| Weight | Access | Notes |
| --- | --- | --- |
| Regular | `IconMonks.house` or `IconMonks.regular.house` | The shorthand works in `const` widgets |
| Thin | `IconMonks.thin.house` | |
| Light | `IconMonks.light.house` | |
| Bold | `IconMonks.bold.house` | |
| Fill | `IconMonks.fill.house` | Solid shapes |

Duotone is not included, because icon fonts are single-color. For duotone, use the SVG files from
[iconmonks.co](https://www.iconmonks.co/) with `flutter_svg`.

## Icon names

Names on the site are kebab-case; in Dart they are camelCase. `arrow-right` becomes `IconMonks.arrowRight`,
`calendar-check` becomes `IconMonks.calendarCheck`. Brand logos end in `Logo`, for example `IconMonks.githubLogo`.

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [Source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
