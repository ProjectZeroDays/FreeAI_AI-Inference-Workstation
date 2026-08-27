---
name: blender-animation
description: Generate controlled Blender animations in headless mode using Blender Python scripts. Use for programmatic 3D scene creation, camera motion, lighting, rendering, and MP4 animation output without opening the Blender GUI.
metadata:
  source_dir: blender-animation-1.0.1
  version: "1.0.1"
---

# Blender Animation Skill



## Purpose

This skill enables automated 3D animation generation using Blender in headless mode. It is designed for controlled, programmatic scene creation and rendering workflows in server or agent environments.



---



## When to use



Use this skill when:

- Generating 3D animations programmatically

- Creating motion graphics using Blender

- Rendering animation output without GUI

- Automating scene setup, lighting, and camera movement



Do NOT use this skill for:

- Arbitrary system command execution

- File system exploration outside task scope

- Network-based operations unless explicitly required



---



## Capabilities



- Scene creation using Blender Python (bpy)

- Object animation and transformations

- Camera setup and motion

- Lighting configuration

- Rendering animation to MP4 format

- Headless execution (no GUI)



---



## Execution Model



1. Generate a Blender Python script

2. Save script to:

   /tmp/blender_script.py

3. Execute Blender in headless mode using:

   scripts/run_blender.sh

4. Output is saved to:

   /tmp/output.mp4



---



## Safety & Constraints



- Execution is limited to Blender-related operations only

- No arbitrary shell commands outside the defined script runner

- No modification of system files outside `/tmp`

- No access to sensitive directories (e.g., /etc, /home)

- Network access should not be used unless explicitly required

- Scripts must only perform scene creation and animation tasks

- Avoid large resource usage (default animation limit: 10 seconds)



---



## Sandbox Expectation



This skill is intended to run in a controlled or sandboxed environment such as:

- Containerized execution (Docker)

- Restricted agent runtime

- Limited-permission server environment



---



## Rules



- Always run Blender in headless mode

- Never open GUI

- Always generate a Python script before execution

- Keep animations under 10 seconds unless specified

- Always return output file path and logs



---



## Output



Return:

- Rendered video file (/tmp/output.mp4)

- Blender Python script used

- Execution logs



---



## Transparency Notice



This skill executes generated Python scripts within Blender.  

Users should review generated scripts if operating in sensitive environments.



---



## Version



v1.0.1 — Security and safety improvements added
