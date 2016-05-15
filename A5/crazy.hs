
import UAIReader

main :: IO ()
main = do
  c <- getChar
  putChar c
  putChar '\n'
  l <- getLine
  putStrLn l
