import kotlin.math.max


fun printBeautyLine(toPrint: String, maxLen : Int) {
    val len = (maxLen - toPrint.length) / 2 - 1

    if (toPrint.isNotEmpty())
        println("\n" + "*".repeat(len) + " $toPrint " + "*".repeat(len) + "\n")
    else
        println("\n" + "*".repeat(maxLen) + "\n")
}


fun beautyPrint(header : String, content : String, footer : String) {
    val maxLen    = max(max(header.length, footer.length), 50)

    printBeautyLine(header, maxLen)
    println(content)
    printBeautyLine(footer, maxLen)
}