# syntax=docker/dockerfile:1.7
#
# Wrapper image for Unraid: the upstream FreeLLMAPI image plus an entrypoint
# that generates ENCRYPTION_KEY on first start when none is provided.
# Nothing is compiled here, so the multi-arch build is a thin layer on top of
# the upstream manifest (linux/amd64 + linux/arm64).
#
# UPSTREAM_TAG is set by the sync workflow to a stable upstream release
# (vX.Y.Z); the default below only exists so a local `docker build .` works.
ARG UPSTREAM_TAG=latest
FROM ghcr.io/tashfeenahmed/freellmapi:${UPSTREAM_TAG}

ARG UPSTREAM_TAG
ARG WRAPPER_REVISION=dev

LABEL org.opencontainers.image.title="FreeLLMAPI (Unraid wrapper)" \
      org.opencontainers.image.description="FreeLLMAPI with automatic ENCRYPTION_KEY generation for Unraid Community Applications" \
      org.opencontainers.image.source="https://github.com/unraid-apps/freellmapi" \
      org.opencontainers.image.url="https://github.com/unraid-apps/freellmapi" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${UPSTREAM_TAG}" \
      org.opencontainers.image.base.name="ghcr.io/tashfeenahmed/freellmapi:${UPSTREAM_TAG}" \
      io.unraid-apps.wrapper.revision="${WRAPPER_REVISION}"

# No RUN steps on purpose: COPY --chmod works for every platform without QEMU.
COPY --chmod=755 entrypoint.sh /usr/local/bin/unraid-entrypoint.sh

# Still root here; the upstream entrypoint drops to the `node` user itself.
USER root
ENTRYPOINT ["/usr/local/bin/unraid-entrypoint.sh"]
CMD ["node", "server/dist/index.js"]
