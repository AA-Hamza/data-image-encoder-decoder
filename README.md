# Simple Text encoder/decoder into an Image
This script just encodes text into an image and can retrieve the text back

## USAGE:
### FOR ENCODING: 
> python3 main.py encode <image name> \[file name\] \[output name\]
### FOR DECODING: 
> python3 main.py decode <image name> \[output file\]

## DEPENDINCIES:
 * Numpy
 * Pillow

## How it works?
It uses 7bits of each pixel to encode the message, to be exact it uses the last 3bits, 2bits, 2bits from each byte of the 3 bytes rgb pixel.
The program stores META data needed for retrivement in the first 2 pixels (The length, The step). The program tries to space out the used pixels so the image don't get much distorted.

## Example
Here is a shrek image

![](readme_data/Shrek.jpg)

We are going to encode the whole transcript of Shrek in the image
using 

```
python3 main.py encode readme_data/Shrek.jpg readme_data/Shrek_transcript readme_data/encoded_shrek.png
```

and here are the result

![](readme_data/encoded_shrek.png)

And you can get the text back by

```
python3 main.py decode readme_data/encoded_shrek.jpg
This is the transcript for the 2001 film, [[Shrek (film)|Shrek]].

==Transcript==
'''[[Shrek (character)|SHREK]]''': (Reading a storybook) Once upon a time there was a [[Storybook Princess|lovely princess]]. But she had an enchantment upon her of a fearful sort which could only be broken by love's first kiss. She was locked away in a castle guarded by a terrible [[Storybook Dragon|fire-breathing dragon]]. Many brave knights had attempted to free her from this dreadful prison, but non prevailed. She waited in the dragon's keep in the highest room of the tallest tower for [[Storybook Prince|her true love]] and true love's first kiss. (Laughs, tears out a pa.....
```
