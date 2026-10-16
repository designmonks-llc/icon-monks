# Monks Icons for Android

Two ways to use the icons, both in this library module:

**Jetpack Compose**

```kotlin
import com.designmonks.icons.MonksIcons

Icon(MonksIcons.Regular.House, contentDescription = "Home")
Icon(MonksIcons.Bold.Heart, contentDescription = null, tint = Color.Red)
Icon(MonksIcons.Duotone.Star, contentDescription = null)
```

**Views / XML**: VectorDrawables named `mi_<name>` (regular) and `mi_<name>_<weight>`.

```xml
<ImageView android:src="@drawable/mi_house" app:tint="@color/brand" />
<ImageView android:src="@drawable/mi_heart_fill" />
```

Drawables use `?attr/colorControlNormal` as their tint, matching Material icons. Copy `src/main/res/drawable` into
your app if you only need a few icons.
