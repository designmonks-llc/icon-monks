// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "MonksIcons",
    platforms: [.iOS(.v14), .macOS(.v11), .tvOS(.v14), .watchOS(.v7)],
    products: [.library(name: "MonksIcons", targets: ["MonksIcons"])],
    targets: [.target(name: "MonksIcons", path: "Sources/MonksIcons", resources: [.process("Resources")])]
)
