# Icon Monks for Android

Published through JitPack. Add the repository and the dependency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement { repositories { google(); mavenCentral(); maven("https://jitpack.io") } }

// app/build.gradle.kts
implementation("com.github.designmonks:icon-monks:v0.2.0")
```

Two ways to use the icons, both in this library:

**Jetpack Compose**

```kotlin
import com.designmonks.icons.IconMonks

Icon(IconMonks.Regular.House, contentDescription = "Home")
Icon(IconMonks.Bold.Heart, contentDescription = null, tint = Color.Red)
Icon(IconMonks.Duotone.Star, contentDescription = null)
```

**Views / XML**: VectorDrawables named `im_<name>` (regular) and `im_<name>_<weight>`.

```xml
<ImageView android:src="@drawable/im_house" app:tint="@color/brand" />
<ImageView android:src="@drawable/im_heart_fill" />
```

Drawables use `?android:attr/colorControlNormal` as their tint, matching Material icons. Copy `src/main/res/drawable` into
your app if you only need a few icons.
