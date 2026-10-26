# Icon Monks for Android

[![JitPack](https://jitpack.io/v/designmonks-llc/icon-monks.svg)](https://jitpack.io/#designmonks-llc/icon-monks)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

6,054 icons for Android in six weights, as Jetpack Compose `ImageVector`s and classic XML `VectorDrawable`s, both in one library. A product of [Design Monks](https://monks.company/). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

## Install

The library is published through JitPack. Add the repository and the dependency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement { repositories { google(); mavenCentral(); maven("https://jitpack.io") } }

// app/build.gradle.kts
implementation("com.github.designmonks-llc:icon-monks:v0.4.1")
```

## Jetpack Compose

Each icon is an extension property in its weight's package, so only the icons you import are compiled into your app.

```kotlin
import com.designmonks.icons.IconMonks
import com.designmonks.icons.regular.House
import com.designmonks.icons.bold.Heart
import com.designmonks.icons.duotone.Star

Icon(IconMonks.Regular.House, contentDescription = "Home")
Icon(IconMonks.Bold.Heart, contentDescription = null, tint = Color.Red)
Icon(IconMonks.Duotone.Star, contentDescription = null)
```

Weights: `Thin`, `Light`, `Regular`, `Bold`, `Fill` and `Duotone`.

## Views and XML

VectorDrawables are named `im_<name>` for regular and `im_<name>_<weight>` for the other weights.

```xml
<ImageView android:src="@drawable/im_house" app:tint="@color/brand" />
<ImageView android:src="@drawable/im_heart_fill" />
```

Drawables use `?android:attr/colorControlNormal` as their tint, matching Material icons. Copy `src/main/res/drawable` into
your app if you only need a few icons.

## Icon names

Names on the website are kebab-case. In Compose they are PascalCase (`arrow-right` is `ArrowRight`), and in XML they
are snake_case with the `im_` prefix (`im_arrow_right`).

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
