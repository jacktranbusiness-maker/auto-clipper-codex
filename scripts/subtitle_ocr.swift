import Foundation
import AVFoundation
import Vision
import CoreGraphics

func fail(_ message: String) -> Never {
    fputs(message + "\n", stderr)
    exit(1)
}
let args = CommandLine.arguments
if args.count != 9 {
    fail("usage: subtitle-ocr input output.tsv step language x y width height")
}
guard let step = Double(args[3]), step.isFinite, step > 0,
      let x = Double(args[5]), let y = Double(args[6]),
      let w = Double(args[7]), let h = Double(args[8]),
      x >= 0, y >= 0, w > 0, h > 0, x + w <= 1, y + h <= 1
else { fail("Invalid step or normalized ROI") }
let output = args[2]
if FileManager.default.fileExists(atPath: output) { fail("Output already exists") }
let asset = AVURLAsset(url: URL(fileURLWithPath: args[1]))
let duration = CMTimeGetSeconds(asset.duration)
if !duration.isFinite || duration <= 0 { fail("Invalid video duration") }
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.maximumSize = CGSize(width: 960, height: 1708)
generator.requestedTimeToleranceBefore = CMTime(value: 1, timescale: 10)
generator.requestedTimeToleranceAfter = CMTime(value: 1, timescale: 10)
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = [args[4]]
request.usesLanguageCorrection = true
request.minimumTextHeight = 0.002
request.regionOfInterest = CGRect(x: x, y: y, width: w, height: h)
if !FileManager.default.createFile(atPath: output, contents: nil) { fail("Cannot create output") }
let handle = try FileHandle(forWritingTo: URL(fileURLWithPath: output))
var frames = 0
var failures = 0
var rows = 0
var nextProgress = 0.0
for second in stride(from: 0.0, to: duration, by: step) {
    autoreleasepool {
        var actualTime = CMTime.zero
        guard let image = try? generator.copyCGImage(
            at: CMTime(seconds: second, preferredTimescale: 600), actualTime: &actualTime)
        else { failures += 1; return }
        let handler = VNImageRequestHandler(cgImage: image)
        do { try handler.perform([request]) }
        catch { failures += 1; return }
        frames += 1
        let text = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
            .joined(separator: " | ")
            .replacingOccurrences(of: "\t", with: " ")
            .replacingOccurrences(of: "\n", with: " ")
        if !text.isEmpty {
            let line = String(format: "%.3f\t%@\n", CMTimeGetSeconds(actualTime), text)
            handle.write(line.data(using: .utf8)!)
            rows += 1
        }
    }
    if second >= nextProgress {
        fputs(String(format: "%.0f / %.0f seconds; failures=%d\n", second, duration, failures), stderr)
        nextProgress += 300
    }
}
try handle.close()
fputs("frames=\(frames) rows=\(rows) failures=\(failures)\n", stderr)
if frames == 0 { fail("No frames recognized successfully") }
