# Claude Omnissiah - Development Notes

## Plugin Development

### Cache Refresh

When updating plugins in the marketplace, **bump the version** in `.claude-plugin/plugin.json` to force a cache refresh. Claude caches plugins at `~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/`.

Without a version bump:
- New files won't appear
- Changes won't take effect
- Users must manually delete the cache

```json
{
  "version": "1.0.0"  →  "version": "1.1.0"
}
```

### Testing Changes

After bumping version, run `/reload-chat` to pick up changes.

## Structure

- `rites/` - Full plugins with agents, commands, hooks, scripts
- `incantations/` - Standalone slash commands
- `marketplace.json` - Plugin registry
