FROM rust:1-bookworm AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY web ./web
COPY curriculum ./curriculum
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 cenere \
    && mkdir /data /training-data \
    && chown cenere:cenere /data /training-data
COPY --from=build /src/target/release/cenere-ai /usr/local/bin/cenere
USER cenere
ENV CENERE_DATA_DIR=/data
EXPOSE 8787
ENTRYPOINT ["cenere"]
