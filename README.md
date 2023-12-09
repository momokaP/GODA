# Midi audiO file eDit Application

* MODA는 간단한 midi파일 파일 편집 기능을 제공합니다. 또한,

* facebookresearch의 demucs의 음원 분리를 소개하고 [demucs](https://github.com/facebookresearch/demucs) 

* spotify의 basic-pitch의 midi/mid 파일 변환을 소개합니다 [basic-pitch](https://github.com/spotify/basic-pitch) 

  

# 주요 기능

* midi파일을 편집합니다

<p align="center">
<img src="./img/주요기능1.png" alt="gimg" width="50%" />
</p>

* demucs 라이브러리를 이용해 음원을 분리 합니다 [demucs](https://github.com/facebookresearch/demucs) github

  <p align="center">
  <img src="./img/주요기능2.png" alt="gimg" width="50%" />
  </p>

* basic-pitch 라이브러리를 이용해 음악파일을 midi 파일로 변환합니다 [basic-pitch](https://github.com/spotify/basic-pitch) github

  <p align="center">
  <img src="./img/주요기능3.png" alt="gimg" width="50%" />
  </p>



# 실행 방법

이 프로젝트는 demucs와 basic-pitch 라이브러리의 용량이 매우 커서 

모두 합치면 2~3 GB크기가 되기 때문에 두 부분으로 나눴습니다

(윈도우 11에서 만든 것이므로 다른 os나 다른 버전에는 실행되지 않을 수 있습니다)

* MID/MIDI 파일 편집기
* 음원분리와 mid로 변환



#### MID/MIDI 파일 편집기 설치

이 프로그램은 sys, PyQt5, numpy, threading, [pretty_midi](https://github.com/craffel/pretty-midi), [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.6/)라이브러리를 사용합니다

version : Python (3.11.2), PyQt5 (5.15.10), numpy (1.26.2), pretty-midi (0.2.10), sounddevice (0.4.6)()



##### 1 실행파일 다운로드 받기 : 오른쪽 Releases에서 다운로드 받을 수 있습니다

* Releases에서 midi_editor.zip 다운 받고 압축 풀기

* 압축 푼 파일을 실행

  <p align="center">
  <img src="./img/실행파일 실행1.png" alt="gimg" width="50%" />
  </p>

  <p align="center">
  <img src="./img/실행파일 실행2.png" alt="gimg" width="50%" />
  </p>

  <p align="center">
  <img src="./img/실행파일 실행3.png" alt="gimg" width="50%" />
  </p>

  

##### 2 실행파일의 바이러스를 의심해서 라이브러리 설치하고 midi_editor.py다운 받아서 실행하기

* midi_editor.py 다운 받기

  

* 라이브러리들 설치하기 ( sys, threading은 표준 라이브러리, 만약 없다면 pip install 해서 설치하기)

  ```
  pip install PyQt5
  ```

  ```
  pip install pretty_midi
  ```

  ```
  pip install sounddevice
  ```

  ```
  pip install numpy
  ```

  

  예시) 

  필요한 라이브러리가 없는 환경에서 실행하면 이렇게 나온다 ( 가상환경으로 예시를 들어봤다 )

  <p align="center">
  <img src="./img/라이브러리부터 설치 예제1.png" alt="gimg" width="50%" />
  </p>

  라이브러리 설치 후 실행한 결과

  <p align="center">
  <img src="./img/라이브러리부터 설치 예제2.png" alt="gimg" width="50%" />
  </p>



#### 음원분리와 mid로 변환 설치

이 프로그램은 sys, PyQt5, demucs, basic_pitch 라이브러리를 사용합니다

version : Python (3.11.2), PyQt5 (5.15.10), 

이 프로그램은 실행 파일로 만들면 용량도 크고 ( 2.5GB 정도 ) 충돌도 많이 있기 때문에

 라이브러리를 설치하고 extract_convert.py을 다운 받아서 실행해주시기 바랍니다



##### 1 라이브러리 설치하고 extract_convert.py다운 받아서 실행하기

* extract_convert.py 다운 받기

* 라이브러리들 설치하기 ( sys는 표준 라이브러리, 만약 없다면 pip install 해서 설치하기)

  ```
  pip install PyQt5
  ```

  ```
  pip install demucs
  ```

  ```
  pip install basic_pitch
  ```

  설치가 꽤 오래 걸릴 겁니다

  

  예시) 

  필요한 라이브러리가 없는 환경에서 실행하면 이렇게 나온다 ( 가상환경으로 예시를 들어봤다 )

  <p align="center">
  <img src="./img/라이브러리부터 설치 예제2_1.png" alt="gimg" width="50%" />
  </p>

  라이브러리 설치 후 실행한 결과

  <p align="center">
  <img src="./img/라이브러리부터 설치 예제2_2.png" alt="gimg" width="50%" />
  </p>

