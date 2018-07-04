# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

import os
import numpy as np

import pyglet
from pyglet.gl import *
from ctypes import byref, POINTER

from .utils import *

class Texture(object):
  """
  Manage the caching of textures, and texture randomization
  """

  # List of textures available for a given path
  tex_paths = {}

  # Cache of textures
  tex_cache = {}

  @classmethod
  def get(self, tex_name, rng=None):
    paths = self.tex_paths.get(tex_name, [])

    # Get an inventory of the existing texture files
    if len(paths) == 0:
      for i in range(1, 10):
        path = get_file_path('textures', '%s_%d' % (tex_name, i), 'png')
        if not os.path.exists(path):
          break
        paths.append(path)

    assert len(paths) > 0, 'failed to load textures for name "%s"' % tex_name

    if rng:
      path_idx = rng.randint(0, len(paths))
      path = paths[path_idx]
    else:
      path = paths[0]

    if path not in self.tex_cache:
      self.tex_cache[path] = Texture(load_texture(path))

    return self.tex_cache[path]

  def __init__(self, tex):
    assert not isinstance(tex, str)
    self.tex = tex

  def bind(self):
    glBindTexture(self.tex.target, self.tex.id)

def load_texture(tex_path):
  img = pyglet.image.load(tex_path)
  tex = img.get_texture()
  glEnable(tex.target)
  glBindTexture(tex.target, tex.id)
  glTexImage2D(
    GL_TEXTURE_2D,
    0,
    GL_RGB,
    img.width,
    img.height,
    0,
    GL_RGBA,
    GL_UNSIGNED_BYTE,
    img.get_image_data().get_data('RGBA', img.width * 4)
  )

  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

  return tex

def create_frame_buffers(width, height, num_samples, return_tex=False):
  """Create the frame buffer objects"""

  # Create a frame buffer (rendering target)
  multi_fbo = GLuint(0)
  glGenFramebuffers(1, byref(multi_fbo))
  glBindFramebuffer(GL_FRAMEBUFFER, multi_fbo)

  # The try block here is because some OpenGL drivers
  # (Intel GPU drivers on macbooks in particular) do not
  # support multisampling on frame buffer objects
  try:
    # Create a multisampled texture to render into
    fbTex = GLuint(0)
    glGenTextures( 1, byref(fbTex));
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, fbTex);
    glTexImage2DMultisample(
      GL_TEXTURE_2D_MULTISAMPLE,
      num_samples,
      GL_RGBA32F,
      width,
      height,
      True
    );
    glFramebufferTexture2D(
      GL_FRAMEBUFFER,
      GL_COLOR_ATTACHMENT0,
      GL_TEXTURE_2D_MULTISAMPLE,
      fbTex,
      0
    );

    # Attach a multisampled depth buffer to the FBO
    depth_rb = GLuint(0)
    glGenRenderbuffers(1, byref(depth_rb))
    glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, num_samples, GL_DEPTH_COMPONENT, width, height);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb);

  except:
    print('Falling back to non-multisampled frame buffer')

    # Create a plain texture texture to render into
    fbTex = GLuint(0)
    glGenTextures( 1, byref(fbTex));
    glBindTexture(GL_TEXTURE_2D, fbTex);
    glTexImage2D(
      GL_TEXTURE_2D,
      0,
      GL_RGBA,
      width,
      height,
      0,
      GL_RGBA,
      GL_FLOAT,
      None
    )
    glFramebufferTexture2D(
      GL_FRAMEBUFFER,
      GL_COLOR_ATTACHMENT0,
      GL_TEXTURE_2D,
      fbTex,
      0
    );

    # Attach depth buffer to FBO
    depth_rb = GLuint(0)
    glGenRenderbuffers(1, byref(depth_rb))
    glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb);

  # Sanity check
  if pyglet.options['debug_gl']:
    res = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    assert res == GL_FRAMEBUFFER_COMPLETE

  # Create the frame buffer used to resolve the final render
  final_fbo = GLuint(0)
  glGenFramebuffers(1, byref(final_fbo))
  glBindFramebuffer(GL_FRAMEBUFFER, final_fbo)

  # Create the texture used to resolve the final render
  fbTex = GLuint(0)
  glGenTextures(1, byref(fbTex))
  glBindTexture(GL_TEXTURE_2D, fbTex)
  glTexImage2D(
    GL_TEXTURE_2D,
    0,
    GL_RGBA,
    width,
    height,
    0,
    GL_RGBA,
    GL_FLOAT,
    None
  )
  glFramebufferTexture2D(
    GL_FRAMEBUFFER,
    GL_COLOR_ATTACHMENT0,
    GL_TEXTURE_2D,
    fbTex,
    0
  )
  if pyglet.options['debug_gl']:
    res = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    assert res == GL_FRAMEBUFFER_COMPLETE

  # Enable depth testing
  glEnable(GL_DEPTH_TEST)

  # Unbind the frame buffer
  glBindFramebuffer(GL_FRAMEBUFFER, 0)

  if return_tex:
    return multi_fbo, final_fbo, fbTex
  else:
    return multi_fbo, final_fbo


class MultiSampleFrameBuffer(object):
  """ Frame buffer class with multi sampling. 

  Arguments:
    width:   Integer, frame buffer width
    height:  Integer, frame buffer height
    num_samples: Integer, multi sampling size
  """
  def __init__(self, width, height, num_samples):
    self.width = width
    self.height = height
    
    self.multi_fbo, self.final_fbo, self.tex = create_frame_buffers(
      width,
      height,
      num_samples,
      return_tex=True
    )

    self.img_array = np.zeros(shape=(height, width, 3), dtype=np.uint8)


  def bind(self):
    glEnable(GL_MULTISAMPLE)
    glBindFramebuffer(GL_FRAMEBUFFER, self.multi_fbo);
    glViewport(0, 0, self.width, self.height)


  def blit(self):
    # Resolve the multisampled frame buffer into the final frame buffer
    glBindFramebuffer(GL_READ_FRAMEBUFFER, self.multi_fbo);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.final_fbo);
    
    glBlitFramebuffer(
      0, 0,
      self.width, self.height,
      0, 0,
      self.width, self.height,
      GL_COLOR_BUFFER_BIT,
      GL_LINEAR
    );


  def read(self):
    self.blit()

    glBindFramebuffer(GL_FRAMEBUFFER, self.final_fbo);
    glReadPixels(
      0,
      0,
      self.width,
      self.height,
      GL_RGB,
      GL_UNSIGNED_BYTE,
      self.img_array.ctypes.data_as(POINTER(GLubyte))
    )

    # Unbind the frame buffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    return self.img_array
