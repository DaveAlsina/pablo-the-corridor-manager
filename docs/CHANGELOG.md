# Changelog

All notable changes to the Corridor Cleaning Bot project will be documented in this file.

## [0.1.0] - 2026-02-01 - Phase 1 MVP

### Added
- ✅ Complete project structure and setup
- ✅ PostgreSQL database with Docker Compose
- ✅ SQLAlchemy ORM with 7 database models
- ✅ Telegram bot with core commands:
  - `/start` - User registration
  - `/help` - Command reference
  - `/status` - Weekly task status
  - `/tasks` - List all available tasks
  - `/complete` - Mark task as complete
  - `/ask` - Get task instructions
  - `/mystats` - Personal statistics
- ✅ Database population script with 22 task types
- ✅ Test data (3 test users)
- ✅ Task opt-out system
- ✅ Setup verification script
- ✅ Comprehensive documentation:
  - README.md (full documentation)
  - QUICKSTART.md (5-minute setup)
  - DEPLOYMENT.md (deployment & testing guide)
  - PROJECT_STRUCTURE.md (architecture overview)
- ✅ Development utilities:
  - Makefile for common commands
  - Database reset script
  - .gitignore configuration
  - Environment template (.env.example)

### Database Schema
- **people** - Corridor residents with Telegram IDs
- **task_types** - 22 predefined cleaning tasks
- **task_opt_outs** - Exemptions for specific tasks
- **weeks** - Weekly cycles with deadlines
- **task_instances** - Specific tasks per week
- **completion_log** - Audit trail for completions
- **penalties** - Reserved for Phase 2

### Task Types Included
- 4 Toilets (1-4)
- 4 Showers (A-D)
- 3 Kitchen tasks (A, E, I)
- 4 Fridges (1-4)
- 2 Hallways (Main, Side)
- 1 Wash room
- 4 Trash tasks (Paper, Glass, Plastic, Kitchen)

### Features
- ✅ User-friendly command interface
- ✅ Partial task name matching
- ✅ Progress tracking per week
- ✅ Personal statistics
- ✅ Multi-user concurrent access
- ✅ Case-insensitive task matching
- ✅ Task completion verification
- ✅ Opt-out enforcement

### Documentation
- Setup guides for beginners and advanced users
- Troubleshooting section
- Database management instructions
- Development workflow guide
- Complete API reference for all commands

## [Upcoming] - Phase 2 - Automation

### Planned Features
- [ ] Scheduled reminders (Wednesday mid-week, Friday final)
- [ ] Automatic week generation (Monday 00:01)
- [ ] Automatic week closing (Friday 12:01)
- [ ] Penalty calculation and tracking
- [ ] Admin commands for manual management
- [ ] Photo evidence upload for tasks
- [ ] Weekly summary reports
- [ ] Backup/restore mechanism

## [Future] - Phase 3 - Analytics

### Planned Features
- [ ] Grafana dashboard
- [ ] Leaderboard system
- [ ] Task difficulty ratings
- [ ] Time-series analysis:
  - Most procrastinated tasks
  - Popular completion days
  - Task completion patterns
  - Individual contribution trends
- [ ] Export functionality (CSV, JSON)
- [ ] Custom report generation

## [Future] - Phase 4 - Advanced Features

### Ideas Under Consideration
- [ ] Task swapping mechanism
- [ ] Points redemption system
- [ ] Integration with building management
- [ ] Mobile app (native or web-based)
- [ ] Multi-corridor support
- [ ] Task templates for different corridor sizes
- [ ] Notification preferences per user
- [ ] Task scheduling (reserve future tasks)
- [ ] Dispute resolution system
- [ ] Reward milestones

---

## Version Notes

**Semantic Versioning:** MAJOR.MINOR.PATCH
- MAJOR: Incompatible API/database changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, backwards compatible

**Current Version:** 0.1.0 (Phase 1 MVP)
**Status:** Beta - Ready for testing with 2-15 users
**Python:** 3.10+
**PostgreSQL:** 16

---

## Migration Notes

### From 0.0.0 to 0.1.0
- Initial release, no migration needed
- Run `python scripts/populate_db.py` for fresh installation

### Future Migrations
Database migrations will be managed via Alembic:
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Known Issues

### Phase 1
- No automatic week management (requires manual creation)
- No scheduled reminders (must check manually)
- No penalty enforcement (database tracks but no automation)
- Week deadline is informational only (doesn't auto-close)
- Photo uploads not implemented (planned for Phase 2)

### Limitations
- Single corridor only (no multi-corridor support)
- No task swapping between users
- No historical analytics (Phase 3 feature)
- Manual opt-out management (no self-service UI)

---

## Contributing

To contribute to this project:
1. Check current version and planned features
2. Review open issues (if using issue tracker)
3. Test changes thoroughly
4. Update this CHANGELOG.md
5. Update documentation if adding features
6. Follow existing code style
7. Add tests for new features

---

## Support

For version-specific issues:
- v0.1.0: See DEPLOYMENT.md for troubleshooting
- Future versions: Check relevant documentation

For general help:
- README.md - Complete documentation
- QUICKSTART.md - Fast setup guide
- PROJECT_STRUCTURE.md - Architecture details
