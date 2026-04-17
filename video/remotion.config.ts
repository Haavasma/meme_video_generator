import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setConcurrency(4);
Config.setOverwriteOutput(true);
// 16:9 landscape is the project default; individual compositions
// can still override via props.
