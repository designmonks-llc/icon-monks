// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "IconMonks",
    platforms: [.iOS(.v14), .macOS(.v11), .tvOS(.v14), .watchOS(.v7)],
    products: [.library(name: "IconMonks", targets: ["IconMonks"])],
    targets: [.target(name: "IconMonks", path: "packages/swift/Sources/IconMonks", resources: [.process("Resources")])]
)
