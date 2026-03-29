FROM node:20-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY apps/content-studio/package.json ./apps/content-studio/
COPY packages/types/package.json ./packages/types/
COPY packages/types/src ./packages/types/src
RUN pnpm install --no-frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/content-studio/node_modules ./apps/content-studio/node_modules
COPY . .
RUN pnpm --filter @agentnext/content-studio build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/content-studio/.next/standalone ./
COPY --from=builder /app/apps/content-studio/.next/static ./apps/content-studio/.next/static
EXPOSE 3600
ENV PORT=3600
CMD ["node", "apps/content-studio/server.js"]
