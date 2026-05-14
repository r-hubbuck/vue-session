<script setup>
defineProps({
  convention: { type: Object, required: true },
})
</script>

<template>
  <!-- Professionalism Policy -->
  <div class="policy-section">
    <h4 class="policy-title">Professionalism Policy</h4>
    <hr class="policy-divider">
    <p class="policy-quote text-muted fst-italic mb-3">
      "...to mark in a fitting manner those who have conferred honor upon their Alma Mater by distinguished scholarship
      and exemplary character as students in engineering, or by their attainments as alumni in the field of engineering..."
    </p>
    <p>This policy defines "exemplary character" in terms of conducting any official <em>Tau Beta Pi</em> business.</p>
    <p>
      All members of <em>Tau Beta Pi</em> shall conduct themselves in a manner consistent with our core membership
      requirements of exemplary character when representing <em>Tau Beta Pi</em> in any public setting. When attending
      any <em>Tau Beta Pi</em> meeting or function, a member of <em>Tau Beta Pi</em> is representing all of our members.
    </p>
    <p>Professional behavior includes but is not limited to the following:</p>

    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-check2-circle me-2" style="color: var(--brand-blue);"></i>Being attentive to the business at hand</div>
      <ul class="policy-list">
        <li>Arriving on time to all scheduled meetings</li>
        <li>Not using electronic devices except for conducting the business at hand or urgent matters</li>
      </ul>
    </div>

    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-check2-circle me-2" style="color: var(--brand-blue);"></i>Being capable to fully discharge your duties</div>
      <ul class="policy-list">
        <li>Arriving mentally and physically alert to all meetings and functions</li>
        <li>Not consuming alcohol prior to or during business meetings or functions</li>
      </ul>
    </div>

    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-check2-circle me-2" style="color: var(--brand-blue);"></i>Being respectful to others in your presence</div>
      <ul class="policy-list">
        <li>Limiting distractions by turning cell phones to off or vibrate (if you must use your phone, briefly excuse yourself from the meeting and return as quickly as possible)</li>
        <li>Dressing appropriately based on the setting (business formal, business casual, casual)</li>
        <li>Not using profanity or expletives</li>
        <li>Being mindful of other attendees, guests, or employees at the meeting location</li>
        <li>Ensuring no damage is done to the facility hosting the meeting or event</li>
      </ul>
    </div>

    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-check2-circle me-2" style="color: var(--brand-blue);"></i>Displaying responsible behavior in social settings associated with the meeting or event</div>
      <ul class="policy-list">
        <li>Not consuming alcohol or other substances to the point of intoxication or impairment</li>
        <li>Not bringing alcohol or other substances to the meetings</li>
        <li>Not bringing outside alcohol or other substances onto the event site</li>
      </ul>
    </div>

    <div class="policy-item" style="background: #fef2f2; border-left-color: #ef4444;">
      <div class="policy-item-title" style="color: #991b1b;"><i class="bi bi-exclamation-circle me-2"></i>Consequences of Violations</div>
      <p class="mb-0" style="font-size: 0.9rem;">
        For all meetings or events, you must be present and on time or considered absent, unless approved by an Association Official.
        Unprofessional behavior will result in dismissal from the event, resulting in an absence. Other consequences are to be
        determined by the Executive Council.
      </p>
    </div>
  </div>

  <!-- Photo Release Policy -->
  <div class="policy-section">
    <h4 class="policy-title">Photo Release Policy</h4>
    <hr class="policy-divider">
    <p>
      I hereby grant permission to <em>Tau Beta Pi</em> to use photographs and/or video of me taken at
      <em>Tau Beta Pi's</em> annual Convention in <strong>{{ convention.location }}</strong>, in publications,
      news releases, online, and in other communications related to the mission of <em>Tau Beta Pi</em>.
    </p>
  </div>

  <!-- Airfare / Cancellation Policy -->
  <div class="policy-section">
    <h4 class="policy-title">Airfare / Cancellation Policy</h4>
    <hr class="policy-divider">
    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-airplane me-2" style="color: var(--brand-blue);"></i>Voting Delegates for Collegiate Chapters</div>
      <p class="mb-0" style="font-size: 0.9rem;">
        If <strong>Tau Beta Pi</strong> purchases your airfare as a voting delegate, these tickets are non-refundable and
        non-transferable. If <strong>Tau Beta Pi</strong> purchases an airline ticket for you and you are unable to attend
        due to illness, bereavement, or weather, please contact HQ immediately. Chapters will be charged for airfare
        purchased on behalf of their members if cancellations are made less than 48 hours prior to the event without a
        valid excuse.
      </p>
    </div>
    <div class="policy-item">
      <div class="policy-item-title"><i class="bi bi-airplane me-2" style="color: var(--brand-blue);"></i>Non-Voting Delegates for Collegiate Chapters</div>
      <p class="mb-0" style="font-size: 0.9rem;">
        Unless otherwise notified, only <strong>ONE</strong> non-voting delegate from each collegiate chapter will be
        reimbursed 20 percent <strong>up to $200</strong> of the airfare purchased.
      </p>
    </div>
  </div>
</template>

<style scoped>
.policy-section {
  margin-bottom: 2rem;
}

.policy-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--brand-blue);
  margin-bottom: 0.5rem;
}

.policy-divider {
  border-color: #e2e8f0;
  margin-bottom: 1.25rem;
}

.policy-quote {
  border-left: 3px solid var(--brand-blue-light);
  padding-left: 1rem;
}

.policy-item {
  background: #fafbfc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid var(--brand-blue-light);
  border-radius: 8px;
  padding: 0.875rem 1rem;
  margin-bottom: 0.75rem;
}

.policy-item-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.policy-list {
  margin: 0;
  padding-left: 1.5rem;
  font-size: 0.875rem;
  color: #4a5568;
}

.policy-list li {
  margin-bottom: 0.25rem;
}
</style>
