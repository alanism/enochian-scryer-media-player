Official OpenSubs CLI runtime, pinned to npm opensubs-cli 0.1.1.
Upstream: https://github.com/opensubtitles-dev/opensubs-cli
License: MIT; see node_modules/opensubs-cli/LICENSE.

Source checkout: npm ci --prefix vlc/subtitle-client
Native dependencies keytar 7.9.0 and platform-folders 0.5.4 are explicitly
approved in package.json. Native compilation needs the normal C++ toolchain
and libsecret headers when a compatible prebuild is unavailable.

The Linux release includes node_modules, so installation needs no npm call.
The app invokes this client only after Download is selected in SUBS.
The client owns provider authentication and quota handling. No user account,
password or token is included in this repository or the Linux release.
