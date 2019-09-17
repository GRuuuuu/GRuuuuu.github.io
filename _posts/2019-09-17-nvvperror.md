---
title: "Nvidia Visual Profiler ERROR : GC Overhead"
categories: 
  - ERROR
tags:
  - NVIDIA
  - JAVA
last_modified_at: 2019-09-17T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


# Environment
`Arch : ppc64le`
`Nvidia Visual Profiler : v10.1`

# ERROR
## 목표
python
## command
~~~
$ nvprof --log-file /tmp/tensorlogs/nvprof/nvprof1.%p.txt --export-profile /tmp/tensorlogs/nvprof/nvprof1.%p.nvvp --print-gpu-trace --profile-child-processes python tf_cnn_benchmarks.py
~~~