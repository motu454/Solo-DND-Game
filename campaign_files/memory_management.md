# Memory Management Protocol

## Information Priority Classification

### **Tier 1: Critical (Always Update in Detail)**
- **Character Progression:** Level advancement, major ability changes, significant equipment acquisition
- **Active Mission Status:** Current objectives, deadlines, critical intelligence developments
- **Major Faction Relationships:** Changes of +/-2 or more trust levels, alliance shifts, enemy neutralization
- **Campaign-Defining Events:** Story developments that alter fundamental campaign direction
- **Resource Status:** Major wealth changes, income modifications, expense restructuring

### **Tier 2: Important (Contextual Detail)**
- **Significant NPC Evolution:** Individual relationship changes of +/-1 trust level
- **Completed Major Quests:** Mission resolution with lasting political or strategic ramifications
- **Strategic Location Changes:** New areas discovered, control status modifications, tactical developments
- **Equipment Modifications:** Items affecting capabilities, magical enhancement, professional gear
- **Network Development:** Asset recruitment, protection upgrades, coordination improvements

### **Tier 3: Background (Summarized)**
- **Minor NPC Interactions:** Conversations without lasting relationship consequences
- **Resolved Plot Threads:** Completed storylines with no ongoing implications for current operations
- **Location Detail Expansions:** Atmospheric information and flavor details for established areas
- **Faction Rumors:** Political intelligence without immediate strategic relevance
- **Routine Operations:** Standard network activities and maintenance procedures

### **Tier 4: Disposable (Omit from Updates)**
- **Pure Flavor Text:** Atmospheric descriptions without mechanical or strategic significance
- **Temporary Tactical Information:** Combat positioning and short-term environmental details
- **Resolved Minor Encounters:** Small-scale interactions with no lasting campaign impact
- **Redundant Information:** Details already captured in other campaign files or sections

---

## Post-Scene Documentation Protocol (During Session)

### **Purpose: Mini-Files for Context Tracking**
Generate session-dated mini-files AFTER scene completion to preserve full context for session-end integration. These mini-files are for DM reference only - player takes no action during session.

### **When to Document (Natural Break Points)**
- **NPCs:** After complete conversations and relationship establishment
- **Locations:** After full exploration and strategic assessment  
- **Plot Developments:** After story revelations conclude and implications become clear
- **Mission Changes:** After objective modifications are fully revealed

### **Mini-File Templates**

#### **For NPCs:**
```
Filename: session[X]-npc-[name].md

# Session [X] NPC: [Name]

## SCENE CONTEXT
[Complete interaction summary, relationship development, opportunities revealed]

## FOR SESSION-END INTEGRATION
### **[Name]** ⭐⭐⭐
- **Role:** [Function based on complete interaction]
- **Relationship:** [Final trust level after full conversation]  
- **Capabilities:** [All abilities/resources revealed]
- **Current Status:** [Situation based on scene conclusion]
- **Intelligence Value:** [Information sources/opportunities]
- **Notes:** [Personality, quirks, motivations from full scene]
```

#### **For Locations:**
```
Filename: session[X]-location-[name].md

# Session [X] Location: [Name]

## EXPLORATION CONTEXT  
[Areas visited, features discovered, political significance identified]

## FOR SESSION-END INTEGRATION
### **[Location]** ⭐⭐⭐
**Type:** [Classification based on complete exploration]
**Control Level:** [Political status after full investigation]
**Overview:** [Complete strategic assessment]
**Key Features:** [All discovered through exploration]  
**Opportunities:** [Revealed through complete scene]
```

### **Benefits of Post-Scene Documentation**
- **Complete Character Understanding:** Full personality, motivations, and relationship dynamics
- **Accurate Strategic Assessment:** All opportunities and threats identified through complete exploration
- **Natural Scene Flow:** No interruptions during dialogue, exploration, or plot development
- **Superior Information Quality:** Documentation based on complete context rather than first impressions

### **Scene Completion Indicators**
**Document NPCs after:**
- Conversation naturally concludes
- Relationship status established
- Scene transitions to new location or activity
- Negotiation or diplomatic exchange completes

**Document Locations after:**
- Area fully explored and mapped
- All significant features discovered
- Political significance understood
- Moving to entirely different location

**Document Plot Developments after:**
- Information revelation completes
- Strategic implications become clear
- Mission parameters fully understood
- Transitioning to next story beat

---

## Session End Integration Protocol

## Session End Integration Protocol

### **Complete Replacement File Generation**
**Generate new campaign files that completely replace existing versions:**

#### **Complete File Merging Process**
1. **Review all session-dated mini-files** (e.g., `session8-npc-hartwick.md`, `session8-location-docks.md`)
2. **Take current campaign files** as base (e.g., `npc-directory.md`, `location-directory.md`)
3. **Merge mini-file content** into current files to create complete updated versions
4. **Generate session-dated complete replacement files:**
   - `npc-directory-session8.md` = current npc-directory.md + all new NPCs from mini-files
   - `location-directory-session8.md` = current location-directory.md + all new locations
   - `active-missions-session8.md` = current active-missions.md + all mission updates
   - `session-log-session8.md` = complete session summary with all events
   - `quick-reference-session8.md` = updated for next session with new additions
   - `campaign-timeline-session8.md` = current timeline + session events
   - Additional files as needed (faction-tracker, character-sheet, etc.)

#### **Player File Replacement Workflow**
**For complete replacement files:**
1. **Download all session-dated complete files** (`*-session8.md`) from artifacts
2. **Add session-dated files to project** - these become your new working campaign files
3. **Archive or delete previous versions** (e.g., `npc-directory-session7.md` or original `npc-directory.md`)
4. **Next session will reference** the session-dated files as current campaign state

#### **File Evolution Example**
**Session 7 → Session 8:**
- **Session 7 ends with:** `npc-directory-session7.md` (your current file)
- **Session 8 mini-files:** `session8-npc-hartwick.md`, `session8-npc-marina.md`
- **Session 8 end generates:** `npc-directory-session8.md` (session7 content + session8 additions)
- **Your new working file:** `npc-directory-session8.md` (complete replacement)
- **Session 9 will reference:** `npc-directory-session8.md` as the current state

#### **Complete Replacement Benefits**
**No Manual Work:**
- **No content copying** - session-dated files are complete and ready to use
- **No merging required** - all integration happens during file generation
- **No manual editing** - download and use session-dated files directly
- **No version confusion** - session-dated file IS the new complete version

**Quality Assurance:**
- **Complete context integration** from all mini-files into existing campaign state
- **Cross-file consistency** verified during generation process
- **All relationships preserved** from previous sessions plus new additions
- **Comprehensive updates** ensure nothing is lost in transition

**Workflow Efficiency:**
- **Single file replacement** rather than content management
- **Clear version progression** from session to session
- **Automatic archival** of previous versions through session dating
- **Next session preparation** built into file generation process

#### **Session End File List**
**Typical complete replacement files generated:**
- `npc-directory-session8.md` - All NPCs (existing + new from session)
- `location-directory-session8.md` - All locations (existing + new from session)
- `active-missions-session8.md` - All missions (existing + updates from session)
- `session-log-session8.md` - Complete session 8 summary
- `quick-reference-session8.md` - Prepared for session 9 with all current info
- `campaign-timeline-session8.md` - All events (existing + session 8 additions)
- `faction-tracker-session8.md` - If relationship changes occurred
- `character-sheet-session8.md` - If character progression/resource changes occurred

**Next session references these session-dated files as the current campaign state.**

### **Cross-Reference Verification Checklist**
- [ ] NPC relationship changes reflected in both npc-directory.md and faction-tracker.md
- [ ] Mission progress updated in both active-missions.md and campaign-timeline.md
- [ ] Character resource changes reflected in character-sheet.md and relevant mission files
- [ ] Location control modifications updated in both location-directory.md and faction-tracker.md
- [ ] New intelligence documented in relevant files and cross-referenced appropriately

---

## Memory Consolidation Strategy

### **Progressive Compression Timeline**
- **Sessions 1-3:** Maintain detailed event records (current campaign position)
- **Sessions 4-6:** Compress to major consequence summaries while preserving relationship impacts
- **Sessions 7+:** Brief outcome documentation unless Tier 1 significance
- **Every 10 Sessions:** Create compressed "historical events" section with major milestones only

### **Detail Retention Guidelines**
- **Recent Sessions (Last 3-4):** Full detail preservation for continuity and reference
- **Medium History (5-10 sessions ago):** Consequence-focused summaries with relationship tracking
- **Distant History (10+ sessions):** Major milestone documentation with brief context
- **Ongoing Relevance:** Maintain detailed records for any information affecting current operations

### **Information Archival Process**
- **Completed Storylines:** Move resolved plot threads to historical summary sections
- **Inactive NPCs:** Compress entries for characters not currently involved in operations
- **Obsolete Intelligence:** Archive tactical information no longer relevant to current missions
- **Superseded Plans:** Remove outdated strategic information replaced by current developments

---

## Cross-Reference Integration

### **Relationship Tracking Coordination**
**When updating NPC relationships:**
- Check [faction-tracker.md](world-state/faction-tracker.md) for broader political implications
- Update [active-missions.md](world-state/active-missions.md) if relationship changes affect objectives
- Modify [location-directory.md](world-state/location-directory.md) if NPC relationship affects area control
- Reference [character-progression.md](character-data/character-progression.md) for character development impact

### **Mission Progress Integration**
**When updating mission status:**
- Check [character-sheet.md](character-data/character-sheet.md) for resource expenditure and capability changes
- Update [npc-directory.md](world-state/npc-directory.md) for relationships affected by mission outcomes
- Modify [faction-tracker.md](world-state/faction-tracker.md) for political consequences of mission completion
- Reference [location-directory.md](world-state/location-directory.md) for territorial or control implications

### **Character Development Tracking**
**When updating character progression:**
- Check [active-missions.md](world-state/active-missions.md) for capability impacts on current objectives
- Update [npc-directory.md](world-state/npc-directory.md) for relationship dynamics affected by advancement
- Modify [faction-tracker.md](world-state/faction-tracker.md) for political standing changes
- Reference [backstory-relationships.md](character-data/backstory-relationships.md) for family reaction updates

---

## Contradiction Resolution Protocol

### **Priority Hierarchy for Conflicting Information**
1. **Recent Player Choices:** Most recent character decisions and stated preferences
2. **Established Character Development:** Consistent personality traits and relationship patterns
3. **Ongoing Relationship Dynamics:** Current NPC attitudes and faction standings
4. **Campaign Timeline:** Previously recorded major events and their documented consequences
5. **Background Information:** Initial setup details and historical context

### **Resolution Process**
1. **Identify Conflict:** Determine specific contradictory elements and their sources
2. **Assess Priority:** Apply hierarchy to determine which information takes precedence
3. **Update Accordingly:** Modify affected files to maintain consistency
4. **Document Resolution:** Note changes made and reasoning in session-log.md
5. **Cross-Check:** Verify resolution doesn't create additional contradictions

### **Prevention Strategies**
- **Consistent Updates:** Use same terminology and relationship scales across all files
- **Regular Cross-Checks:** Verify new information against existing records before finalizing
- **Clear Documentation:** Note reasoning for major changes to support future consistency
- **Systematic Reviews:** Periodic comprehensive review of all files for consistency maintenance

---

## World Progression Integration

### **Time-Based Update Triggers**
**Session Gaps (Extended Time Passage):**
- Update [faction-tracker.md](world-state/faction-tracker.md) for independent faction goal advancement
- Modify [npc-directory.md](world-state/npc-directory.md) for personal goal progression and relationship evolution
- Update [location-directory.md](world-state/location-directory.md) for environmental changes and control shifts
- Reference [world-progression.md](frameworks/world-progression.md) for systematic development guidelines

### **Butterfly Effect Documentation**
**Track Consequence Chains:**
- Document how minor player actions create major long-term consequences
- Record delayed outcomes emerging 2-3 sessions after original decisions
- Identify unexpected beneficiaries and victims of character choices
- Note cascade effects through political, economic, and supernatural networks

### **NPC Development Tracking**
**Independent Character Growth:**
- Update personal goal advancement for significant NPCs regardless of player interaction
- Track relationship evolution between NPCs independent of character involvement
- Document career advancement, status changes, and new alliance formation
- Record how world events affect individual NPC circumstances and attitudes

---

## Archival and Backup Procedures

### **Session Backup Creation**
**After each session:**
- Create complete file snapshot in archive/session-[number]-backup/ directory
- Include all eight core campaign files with current version numbers
- Document major changes made during session in backup directory readme
- Maintain backup accessibility for reference and error recovery

### **Version Control Guidelines**
- **File Naming:** Use descriptive names without version numbers in primary directory
- **Change Documentation:** Record significant modifications in session-log.md
- **Backup Reference:** Maintain clear backup organization for historical reference
- **Recovery Protocols:** Establish procedures for reverting problematic changes

### **Archive Organization**
```
archive/
├── session-01-backup/
├── session-02-backup/
├── session-07-backup/    # Current state backup
├── session-08-backup/    # Next session backup
└── deprecated-content/   # Obsolete information storage
```

---

## Quality Assurance Checklist

### **Update Completion Verification**
- [ ] All eight core files updated with session information
- [ ] Cross-references verified for consistency across files
- [ ] Relationship changes properly documented in all relevant locations
- [ ] Mission progress accurately reflected in multiple file systems
- [ ] Character development impacts distributed to appropriate files

### **Information Priority Application**
- [ ] Tier 1 information updated with complete detail
- [ ] Tier 2 information summarized with appropriate context
- [ ] Tier 3 information compressed to essential elements
- [ ] Tier 4 information excluded from permanent records

### **Consistency Maintenance**
- [ ] No contradictions between relationship assessments across files
- [ ] Mission status consistent between active-missions.md and other references
- [ ] Character capabilities accurately reflected in all relevant contexts
- [ ] Political standings coordinated between faction-tracker.md and npc-directory.md

---

**Implementation Notes:**
- Apply classification system consistently to maintain manageable file sizes
- Use cross-reference verification to prevent information inconsistencies
- Focus updates on consequence-relevant information rather than exhaustive detail documentation
- Maintain archival procedures for reference and error recovery capabilities
- Prioritize recent player choices and character development over background consistency when conflicts arise