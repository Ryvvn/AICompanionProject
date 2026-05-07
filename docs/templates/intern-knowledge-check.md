# Post-Epic Intern Knowledge Check Template

*Facilitator Note: This document is to be filled out by a Senior Developer or Architect after the completion of an Epic. It serves as a comprehension check for interns or junior developers to ensure they understand the architectural intent, trade-offs, and implementation details of the Epic.*

## Epic Details
- **Epic Number:** [Epic Number]
- **Epic Name:** [Epic Name]
- **Intern/Junior Dev:** [Name]
- **Reviewer:** [Name]

---

## Part 1: Architecture & Design Decisions
*Questions to verify understanding of structural choices.*

1. **Why did we build [Specific Component/Module] the way we did instead of [Alternative Approach]?**
   - *Expected understanding:* [Brief note on trade-offs]
2. **Where does the code for [Specific Feature] live, and why does it belong in that specific module?**
   - *Expected understanding:* [Understanding of boundaries and separation of concerns]
3. **If a new requirement came in to add [Hypothetical Feature related to the Epic], how would our current architecture support or restrict it?**
   - *Expected understanding:* [Understanding of extensibility]
4. **Explain the data flow when [Specific Action] happens in this Epic.**
   - *Expected understanding:* [Ability to trace a request/event end-to-end]

## Part 2: State & Data Management
*Questions to verify understanding of persistence and mutability.*

5. **Where is the data for [Specific Feature] stored, and what format is it in?**
   - *Expected understanding:* [Knowledge of local files, JSON, YAML, etc.]
6. **Why did we choose to enforce [Specific Rule, e.g., Canonical States] rather than allowing dynamic inputs?**
   - *Expected understanding:* [Predictability and testing ease]
7. **If the application crashes while [Specific Process] is running, what happens to the data?**
   - *Expected understanding:* [Understanding of atomicity, file safety, or acceptable loss]

## Part 3: Integrations & Error Handling
*Questions to verify understanding of resilience.*

8. **How does the system behave if [Specific Integration/Service] goes offline or returns an error?**
   - *Expected understanding:* [Graceful degradation, fallback modes]
9. **Where do we log errors for [Specific Component], and what information is included in those logs?**
   - *Expected understanding:* [Diagnostic visibility and event logging]
10. **Explain the purpose of the adapter pattern used for [Specific Integration].**
    - *Expected understanding:* [Isolation of third-party dependencies]

## Part 4: Product & User Experience
*Questions to verify understanding of the "Why" behind the feature.*

11. **What specific user problem (from the PRD) does this Epic solve?**
    - *Expected understanding:* [Connecting code to business value]
12. **How does the user interact with the features built in this Epic?**
    - *Expected understanding:* [CLI commands, dashboard views, text inputs]
13. **What are the privacy implications of the data we capture in this Epic, and how did we mitigate them?**
    - *Expected understanding:* [Local-first principles, allowed categories]

## Part 5: Testing & Quality
*Questions to verify understanding of verification.*

14. **What was the most complex scenario to test in this Epic, and how did we validate it?**
    - *Expected understanding:* [Awareness of edge cases]
15. **If you had to write an automated test for [Specific Feature], what would you mock or stub?**
    - *Expected understanding:* [Test isolation]

---

## Reviewer Sign-off
- [ ] Intern demonstrated solid understanding of the architecture.
- [ ] Intern understood the product value and UX constraints.
- [ ] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** [List any specific documentation or code the intern should review further]
