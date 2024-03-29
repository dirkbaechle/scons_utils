import scala.xml._
import scala.collection.mutable.HashMap
import swing._

import java.io.File

object SConsCommon {
  // Set of common English words to exclude from the word counting.
  val commonEnglishWords : Set[String] = "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(",").toSet

  /** Simplify a String by removing all non-alphanumerical chars. */
  def defaultSimplify(word : String) : String =
  {
      return word.replaceAll("[^\\p{L}\\p{Nd}]", " ")
  }

}

/** A single message in a Thread. */
case class SConsMessage(val header : String,
                   val author : String,
                   val fullname : String,
                   val date : String,
                   val content : String)
{

    /** Scan the content of the message and update word counts with it. */ 
    def collectWordCounts(wordCounts : HashMap[String, Int],
                          accept : SConsMessage => Boolean,
                          excludeWords : Set[String],
                          simplifyString : String => String = SConsCommon.defaultSimplify) 
    {
        // Skip message, if accept criterion doesn't match
        if (!accept(this))
            return

        // Simplify content and split it into words
        val words = simplifyString(this.content).split("\\s").toList.map(_.asInstanceOf[String])
        // Process each word and update count hash
        words.foreach(w => if (!w.isEmpty && !excludeWords.contains(w.toLowerCase()))
                           {
                               if (wordCounts.contains(w))
                                   wordCounts(w) += 1
                               else
                                   wordCounts += (w -> 1)
                           }
                     )
    }
}

/** A single thread, containing one or more messages. */
case class SConsThread(val html : String,
                  val id : String,
                  val issue : String,
                  val messages : Seq[SConsMessage])
{
    /** Scan all contained messages and update word counts accordingly. */
    def collectWordCounts(wordCounts : HashMap[String, Int],
                          accept : SConsMessage => Boolean,
                          excludeWords : Set[String]) 
    {
        this.messages.foreach(m => m.collectWordCounts(wordCounts, accept, excludeWords))
    }

}

/** Set of all threads in a mailing list like "devel" or "user". */
class SConsThreadList
{
    var threads : List[SConsThread] = Nil
    /** Parse the given XML file and store the contained message threads. */
    def loadXml(fpath : String)
    {
      val domElems = scala.xml.XML.loadFile(fpath)
      this.threads = (domElems \ "thread").map { thread =>
                      val html = (thread \ "html").text
                      val id = (thread \ "id").text
                      val issue = (thread \ "issue").text
                      val msglist = (thread \ "messages" \ "message").map {message =>

                        val header = (message \ "header").text
                        val author = (message \ "author").text
                        val fullname = (message \ "fullname").text
                        val date = (message \ "date").text
                        val content = (message \ "content").text
                        SConsMessage(header, author, fullname, date, content)
                      }
                      SConsThread(html, id, issue, msglist)
                    }.toList
    }

    /** Return a HashMap that results from counting the occurence of each word,
        in all the messages that get selected by the accept method. */
    def getWordCounts(accept : SConsMessage => Boolean,
                      excludeWords : Set[String]) : HashMap[String, Int] =
    {
        var wordCounts = new HashMap[String, Int]
        this.threads.foreach(t => t.collectWordCounts(wordCounts, accept, excludeWords))
        return wordCounts        
    }
}

//val dev = new SConsThreadList("devel.xml")
//println("Developer threads: "+dev.threads.size)

//val user = new SConsThreadList("user.xml")
//println("User threads: "+user.threads.size)
//println(user.getWordCounts(SConsCommon.commonEnglishWords).toList sortBy {_._2})


object Starter {
  def main(args: Array[String]): Unit = {
    val archiveViewer = new SConsArchives()
    archiveViewer.visible = true
  }
}


class SConsArchives extends Frame
{
  title = "SConsArchiveViewer"

  // Data lists
  val threadData = new SConsThreadList
  var keywordData = new HashMap[String, Int]

  // Search panel
  val searchField = new TextField("")
  val keyView = new ListView[String]()
  val searchPanel = new BoxPanel(Orientation.Vertical) {
          // Search keywords
          contents += new BoxPanel(Orientation.Horizontal) {
            contents += new Label("Search:")
            contents += searchField
            }
          contents += new ScrollPane(keyView)
  }
 
  // Thread list
  val threadView = new ListView[String]()
  val threadPane = new ScrollPane(threadView)

  // Message list
  val messageView = new ListView[String]()
  val messagePane = new ScrollPane(messageView)
  
  // Editor panel
  val messageEditor = new EditorPane()
  val editPane = new ScrollPane(messageEditor)

  contents = new SplitPane(Orientation.Vertical,
               // Left stack
               new SplitPane(Orientation.Horizontal, searchPanel, threadPane),
               new SplitPane(Orientation.Horizontal, messagePane, editPane))

  // How to resize a SplitPane, based on ratio
  //
  // oneTouchExpandable = true
  // resizeWeight = 0.5
  // leftComponent.preferredSize = 0 -> 0
  // rightComponent.preferredSize = 0 -> 0
  //


  def updateKeywordList(keyprefix : String) {
      var keylist = this.keywordData.toList.sortBy(_._2)(Ordering[Int].reverse)
      if (!keyprefix.isEmpty)
          this.keyView.listData = keylist.filter(k => k._1.toLowerCase().startsWith(keyprefix.toLowerCase())).map{ case (k, v) => k + ", " + v}
      else
          this.keyView.listData = keylist.map{ case (k, v) => k + ", " + v}
  }

  // Simple comparator that will match all messages
  def acceptAll(m : SConsMessage) : Boolean = {
      return true
  }

  // Adding menus
  val quitAction = Action("Quit") {System.exit(0)}
  val openAction = Action("Open") {
    val chooser = new FileChooser(new File("."))
    chooser.title = "Select input file"
    val result = chooser.showOpenDialog(null)
    if (result == FileChooser.Result.Approve) {
      println("Loading file -- " + chooser.selectedFile.getName)
      threadData.loadXml(chooser.selectedFile.getName)
      keywordData = threadData.getWordCounts(acceptAll, SConsCommon.commonEnglishWords)
      searchField.text = ""
      this.updateKeywordList(searchField.text)
    } else None
  }
  menuBar = new MenuBar{
         contents += new Menu("File") {
            contents += new MenuItem(openAction)
            contents += new Separator
            contents += new MenuItem(quitAction)
         }
  } 

}

