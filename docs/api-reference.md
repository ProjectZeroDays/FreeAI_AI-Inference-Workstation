# FreeAI Dashboard API Reference

**Version:** 1.0
**Total Endpoints:** 562

---

## `GET` /

- **Endpoint:** `index`

---

## `GET` /admin/hot-models

- **Endpoint:** `admin_hot_models_page`

---

## `POST` /admin/hot-models

- **Endpoint:** `admin_hot_models_load`

---

## `DELETE` /admin/hot-models/<model_id>

- **Endpoint:** `admin_hot_models_unload`

---

## `POST` /admin/hot-models/health

- **Endpoint:** `admin_hot_models_health`

---

## `POST` /admin/model-switch

- **Endpoint:** `admin_model_switch`

---

## `GET` /ai-red-teaming

- **Endpoint:** `page_ai_red_teaming`

---

## `GET` /ai-training

- **Endpoint:** `ai_training_page`

---

## `GET` /aikido

- **Endpoint:** `aikido_page`

---

## `GET` /api/agents/list

Return active agents.

- **Endpoint:** `api_agents_list`

---

## `GET` /api/ai-redteam/campaigns

- **Endpoint:** `api_ai_redteam_campaigns`

---

## `POST` /api/ai-redteam/remediate

- **Endpoint:** `api_ai_redteam_remediate`

---

## `GET` /api/ai-redteam/results

- **Endpoint:** `api_ai_redteam_results`

---

## `POST` /api/ai-redteam/start

- **Endpoint:** `api_ai_redteam_start`

---

## `GET` /api/aikido

- **Endpoint:** `api_aikido`

---

## `POST` /api/aikido/scan

- **Endpoint:** `api_aikido_scan`

---

## `GET` /api/aikido/settings

- **Endpoint:** `api_aikido_settings`

---

## `POST` /api/aikido/settings

- **Endpoint:** `api_aikido_settings_save`

---

## `POST` /api/aikido/test

- **Endpoint:** `api_aikido_test`

---

## `GET` /api/alerts

Return active alerts.

- **Endpoint:** `api_alerts`

---

## `GET` /api/analytics/alerts

- **Endpoint:** `api_analytics_alerts`

---

## `POST` /api/analytics/predict

- **Endpoint:** `api_analytics_predict`

---

## `GET` /api/analytics/risk-score

- **Endpoint:** `api_analytics_risk_score`

---

## `GET` /api/analytics/trends

- **Endpoint:** `api_analytics_trends`

---

## `POST` /api/android-exploit/bluetooth

- **Endpoint:** `api_android_exploit_bluetooth`

---

## `GET` /api/android-exploit/cves

- **Endpoint:** `api_android_exploit_cves`

---

## `GET` /api/android-exploit/describe

- **Endpoint:** `api_android_exploit_describe`

---

## `POST` /api/android-exploit/image

- **Endpoint:** `api_android_exploit_image`

---

## `POST` /api/android-exploit/kernel

- **Endpoint:** `api_android_exploit_kernel`

---

## `POST` /api/android-exploit/mms

- **Endpoint:** `api_android_exploit_mms`

---

## `POST` /api/android-exploit/nfc

- **Endpoint:** `api_android_exploit_nfc`

---

## `POST` /api/apt/feed/refresh

- **Endpoint:** `api_apt_feed_refresh`

---

## `GET` /api/apt/groups

- **Endpoint:** `api_apt_groups`

---

## `GET` /api/apt/threats

- **Endpoint:** `api_apt_threats`

---

## `GET` /api/apt/ttps

- **Endpoint:** `api_apt_ttps`

---

## `POST` /api/audit/clear

- **Endpoint:** `api_audit_clear`

---

## `POST` /api/audit/query

- **Endpoint:** `api_audit_query`

---

## `GET` /api/audit/summary

- **Endpoint:** `api_audit_summary`

---

## `GET` /api/automations

- **Endpoint:** `api_automations_list`

---

## `POST` /api/automations

- **Endpoint:** `api_automation_create`

---

## `DELETE` /api/automations/<job_id>

- **Endpoint:** `api_automation_delete`

---

## `POST` /api/automations/<job_id>/run

- **Endpoint:** `api_automation_run_now`

---

## `POST` /api/automations/<job_id>/toggle

- **Endpoint:** `api_automation_toggle`

---

## `GET` /api/automations/history

- **Endpoint:** `api_automation_history`

---

## `GET` /api/automations/stats

- **Endpoint:** `api_automation_stats`

---

## `POST` /api/automobile-exploit/can-inject

- **Endpoint:** `api_automobile_exploit_can_inject`

---

## `GET` /api/automobile-exploit/cves

- **Endpoint:** `api_automobile_exploit_cves`

---

## `GET` /api/automobile-exploit/describe

- **Endpoint:** `api_automobile_exploit_describe`

---

## `POST` /api/automobile-exploit/infotainment

- **Endpoint:** `api_automobile_exploit_infotainment`

---

## `POST` /api/automobile-exploit/keyless

- **Endpoint:** `api_automobile_exploit_keyless`

---

## `POST` /api/automobile-exploit/obd2

- **Endpoint:** `api_automobile_exploit_obd2`

---

## `POST` /api/automobile-exploit/telematics

- **Endpoint:** `api_automobile_exploit_telematics`

---

## `POST` /api/bluetooth-exploit/ble-deauth

- **Endpoint:** `api_bluetooth_exploit_ble_deauth`

---

## `POST` /api/bluetooth-exploit/ble-sniff

- **Endpoint:** `api_bluetooth_exploit_ble_sniff`

---

## `POST` /api/bluetooth-exploit/blueborne

- **Endpoint:** `api_bluetooth_exploit_blueborne`

---

## `GET` /api/bluetooth-exploit/cves

- **Endpoint:** `api_bluetooth_exploit_cves`

---

## `GET` /api/bluetooth-exploit/describe

- **Endpoint:** `api_bluetooth_exploit_describe`

---

## `POST` /api/bluetooth-exploit/keyless

- **Endpoint:** `api_bluetooth_exploit_keyless`

---

## `GET` /api/browser/reset

- **Endpoint:** `reset_browser_settings`

---

## `GET` /api/browser/settings

- **Endpoint:** `get_browser_settings`

---

## `POST` /api/browser/settings

- **Endpoint:** `save_browser_settings`

---

## `GET` /api/browser/status

- **Endpoint:** `api_browser_status`

---

## `GET` /api/bt-scan/devices

- **Endpoint:** `api_bt_scan_devices`

---

## `GET` /api/c2/events

- **Endpoint:** `api_c2_events`

---

## `POST` /api/c2/scan

- **Endpoint:** `api_c2_scan`

---

## `POST` /api/c2/shell

- **Endpoint:** `api_c2_shell`

---

## `GET` /api/campaign

- **Endpoint:** `api_campaign`

---

## `DELETE` /api/campaign/<campaign_id>

- **Endpoint:** `api_campaign_delete`

---

## `POST` /api/campaign/<campaign_id>/run

- **Endpoint:** `api_campaign_run`

---

## `POST` /api/campaign/create

- **Endpoint:** `api_campaign_create`

---

## `GET` /api/campaigns

Return campaign list.

- **Endpoint:** `api_campaigns`

---

## `DELETE` /api/campaigns/<id>/delete

Delete a campaign.

- **Endpoint:** `api_campaigns_delete`

---

## `POST` /api/campaigns/<id>/toggle

Toggle campaign status.

- **Endpoint:** `api_campaigns_toggle`

---

## `POST` /api/campaigns/create

Create a new campaign.

- **Endpoint:** `api_campaigns_create`

---

## `GET` /api/cards/settings

- **Endpoint:** `api_cards_settings`

---

## `GET` /api/cards/settings/<card_name>

- **Endpoint:** `api_cards_settings_get`

---

## `PUT` /api/cards/settings/<card_name>

- **Endpoint:** `api_cards_settings_update`

---

## `GET` /api/clients

- **Endpoint:** `api_clients`

---

## `GET` /api/cloud/configs

- **Endpoint:** `api_cloud_configs`

---

## `POST` /api/cloud/exploit-sim

- **Endpoint:** `api_cloud_exploit_sim`

---

## `GET` /api/cloud/iam

- **Endpoint:** `api_cloud_iam`

---

## `POST` /api/cloud/scan

- **Endpoint:** `api_cloud_scan`

---

## `GET` /api/comm/config

- **Endpoint:** `communications.comm_get_config`

---

## `POST` /api/comm/config

- **Endpoint:** `communications.comm_save_config`

---

## `GET` /api/comm/messages

- **Endpoint:** `communications.comm_messages`

---

## `POST` /api/comm/messages/clear

- **Endpoint:** `communications.comm_clear_messages`

---

## `GET` /api/comm/providers

- **Endpoint:** `communications.comm_list_providers`

---

## `GET` /api/comm/providers/<pid>

- **Endpoint:** `communications.comm_get_provider`

---

## `POST` /api/comm/providers/<pid>/configure

- **Endpoint:** `communications.comm_configure_provider`

---

## `POST` /api/comm/providers/<pid>/connect

- **Endpoint:** `communications.comm_connect_provider`

---

## `POST` /api/comm/providers/<pid>/disconnect

- **Endpoint:** `communications.comm_disconnect_provider`

---

## `GET` /api/comm/providers/<pid>/health

- **Endpoint:** `communications.comm_health_provider`

---

## `POST` /api/comm/providers/<pid>/test

- **Endpoint:** `communications.comm_test_provider`

---

## `POST` /api/comm/providers/test-all

- **Endpoint:** `communications.comm_test_all`

---

## `GET` /api/comm/receive/<pid>

- **Endpoint:** `communications.comm_receive`

---

## `POST` /api/comm/send

- **Endpoint:** `communications.comm_send`

---

## `GET` /api/comm/stats

- **Endpoint:** `communications.comm_stats`

---

## `GET` /api/config

- **Endpoint:** `get_config`

---

## `GET` /api/configs

- **Endpoint:** `api_configs_list`

---

## `GET` /api/configs/<path:name>

- **Endpoint:** `api_configs_get`

---

## `DELETE` /api/configs/<path:name>

- **Endpoint:** `api_configs_delete`

---

## `POST` /api/configs/backup

- **Endpoint:** `api_configs_backup`

---

## `GET` /api/configs/backups/<path:name>

- **Endpoint:** `api_configs_backups_list`

---

## `POST` /api/configs/backups/<path:name>/<path:backup_name>

- **Endpoint:** `api_configs_backup_restore`

---

## `GET` /api/crashes

- **Endpoint:** `api_crashes`

---

## `GET` /api/crashes/<filename>

- **Endpoint:** `api_crash_detail`

---

## `POST` /api/crashes/prune

- **Endpoint:** `api_crashes_prune`

---

## `GET` /api/dashboard/jobs

Return recent jobs for dashboard.

- **Endpoint:** `api_dashboard_jobs`

---

## `GET` /api/dashboard/overview

Return unified dashboard overview data.

- **Endpoint:** `api_dashboard_overview`

---

## `POST` /api/ddns/provision

- **Endpoint:** `api_ddns_provision`

---

## `GET` /api/ddns/records

- **Endpoint:** `api_ddns_records`

---

## `PUT` /api/ddns/records/<record_id>

- **Endpoint:** `api_ddns_update_record`

---

## `GET` /api/ddns/status

- **Endpoint:** `api_ddns_status`

---

## `GET` /api/ddns/sync

- **Endpoint:** `api_ddns_sync`

---

## `GET` /api/dependency/describe

- **Endpoint:** `api_dependency_describe`

---

## `POST` /api/dependency/patch

- **Endpoint:** `api_dependency_patch`

---

## `GET` /api/dependency/plugins

- **Endpoint:** `api_dependency_plugins`

---

## `GET` /api/dependency/resources

- **Endpoint:** `api_dependency_resources`

---

## `GET, POST` /api/dependency/settings

- **Endpoint:** `api_dependency_settings`

---

## `POST` /api/encryption/check-passphrase

- **Endpoint:** `api_encryption_check_passphrase`

---

## `GET` /api/encryption/disks

Return LUKS status and block device info for all disks.

- **Endpoint:** `api_encryption_disks`

---

## `POST` /api/encryption/encrypt-disk

Encrypt a disk with LUKS (dry-run safe on non-/dev/* paths).

- **Endpoint:** `api_encryption_encrypt_disk`

---

## `POST` /api/encryption/recovery-key

Generate a random recovery key for LUKS encryption.

- **Endpoint:** `api_encryption_recovery_key`

---

## `GET` /api/errors

- **Endpoint:** `api_errors`

---

## `POST` /api/errors/ack/<err_id>

- **Endpoint:** `api_errors_ack`

---

## `POST` /api/errors/clear

- **Endpoint:** `api_errors_clear`

---

## `GET` /api/errors/export

- **Endpoint:** `api_errors_export`

---

## `GET` /api/errors/stats

- **Endpoint:** `api_errors_stats`

---

## `GET` /api/evals/history

Return raw history entries.

- **Endpoint:** `api_evals_history`

---

## `GET` /api/evals/leaderboard

Return leaderboard summary from history.

- **Endpoint:** `api_evals_leaderboard`

---

## `GET` /api/evals/results/<run_id>

Return full results for a specific run.

- **Endpoint:** `api_evals_results`

---

## `POST` /api/evals/run

Trigger a new eval run (sync or async).

- **Endpoint:** `api_evals_run`

---

## `GET` /api/evals/runs

- **Endpoint:** `api_evals_runs`

---

## `GET` /api/evals/tasks

Return the golden task definitions.

- **Endpoint:** `api_evals_tasks`

---

## `POST` /api/exploit-cat/chained-zero-day/analyze-chain

- **Endpoint:** `api_exploit_cat_chained_zero_day_analyze_chain`

---

## `POST` /api/exploit-cat/chained-zero-day/build-chain

- **Endpoint:** `api_exploit_cat_chained_zero_day_build_chain`

---

## `GET` /api/exploit-cat/chained-zero-day/cves

- **Endpoint:** `api_exploit_cat_chained_zero_day_cves`

---

## `GET` /api/exploit-cat/chained-zero-day/describe

- **Endpoint:** `api_exploit_cat_chained_zero_day_describe`

---

## `GET` /api/exploit-cat/chained-zero-day/list-chains

- **Endpoint:** `api_exploit_cat_chained_zero_day_list_chains`

---

## `POST` /api/exploit-cat/chained-zero-day/optimize-chain

- **Endpoint:** `api_exploit_cat_chained_zero_day_optimize_chain`

---

## `POST` /api/exploit-cat/chained-zero-day/simulate-chain

- **Endpoint:** `api_exploit_cat_chained_zero_day_simulate_chain`

---

## `GET` /api/exploit-cat/deserialization-exploit/cves

- **Endpoint:** `api_deserialization_exploit_cves`

---

## `GET` /api/exploit-cat/deserialization-exploit/describe

- **Endpoint:** `api_deserialization_exploit_describe`

---

## `POST` /api/exploit-cat/deserialization-exploit/generate-payload

- **Endpoint:** `api_deserialization_exploit_generate_payload`

---

## `GET` /api/exploit-cat/deserialization-exploit/primitives

- **Endpoint:** `api_deserialization_exploit_primitives`

---

## `POST` /api/exploit-cat/deserialization-exploit/simulate-java

- **Endpoint:** `api_deserialization_exploit_simulate_java`

---

## `POST` /api/exploit-cat/deserialization-exploit/simulate-python

- **Endpoint:** `api_deserialization_exploit_simulate_python`

---

## `GET` /api/exploit-cat/file-parse-exploit/cves

- **Endpoint:** `api_file_parse_exploit_cves`

---

## `GET` /api/exploit-cat/file-parse-exploit/describe

- **Endpoint:** `api_file_parse_exploit_describe`

---

## `POST` /api/exploit-cat/file-parse-exploit/generate-payload

- **Endpoint:** `api_file_parse_exploit_generate_payload`

---

## `GET` /api/exploit-cat/file-parse-exploit/primitives

- **Endpoint:** `api_file_parse_exploit_primitives`

---

## `POST` /api/exploit-cat/file-parse-exploit/simulate-email

- **Endpoint:** `api_file_parse_exploit_simulate_email`

---

## `POST` /api/exploit-cat/file-parse-exploit/simulate-office

- **Endpoint:** `api_file_parse_exploit_simulate_office`

---

## `POST` /api/exploit-cat/file-parse-exploit/simulate-pdf

- **Endpoint:** `api_file_parse_exploit_simulate_pdf`

---

## `POST` /api/exploit-cat/file-parse-exploit/simulate-xxe

- **Endpoint:** `api_file_parse_exploit_simulate_xxe`

---

## `GET` /api/exploit-cat/media-exploit/cves

- **Endpoint:** `api_media_exploit_cves`

---

## `GET` /api/exploit-cat/media-exploit/describe

- **Endpoint:** `api_media_exploit_describe`

---

## `POST` /api/exploit-cat/media-exploit/generate-payload

- **Endpoint:** `api_media_exploit_generate_payload`

---

## `GET` /api/exploit-cat/media-exploit/primitives

- **Endpoint:** `api_media_exploit_primitives`

---

## `POST` /api/exploit-cat/media-exploit/simulate-audio

- **Endpoint:** `api_media_exploit_simulate_audio`

---

## `POST` /api/exploit-cat/media-exploit/simulate-image

- **Endpoint:** `api_media_exploit_simulate_image`

---

## `POST` /api/exploit-cat/media-exploit/simulate-video

- **Endpoint:** `api_media_exploit_simulate_video`

---

## `GET` /api/exploit-cat/memory-corruption/cves

- **Endpoint:** `api_memory_corruption_cves`

---

## `GET` /api/exploit-cat/memory-corruption/describe

- **Endpoint:** `api_memory_corruption_describe`

---

## `POST` /api/exploit-cat/memory-corruption/generate-payload

- **Endpoint:** `api_memory_corruption_generate_payload`

---

## `GET` /api/exploit-cat/memory-corruption/primitives

- **Endpoint:** `api_memory_corruption_primitives`

---

## `POST` /api/exploit-cat/memory-corruption/simulate-buffer-overflow

- **Endpoint:** `api_memory_corruption_simulate_buffer_overflow`

---

## `POST` /api/exploit-cat/memory-corruption/simulate-format-string

- **Endpoint:** `api_memory_corruption_simulate_format_string`

---

## `POST` /api/exploit-cat/memory-corruption/simulate-heap-corruption

- **Endpoint:** `api_memory_corruption_simulate_heap_corruption`

---

## `POST` /api/exploit-cat/memory-corruption/simulate-uaf

- **Endpoint:** `api_memory_corruption_simulate_uaf`

---

## `GET` /api/exploit-cat/memory-primitives/<name>

- **Endpoint:** `api_exploit_cat_memory_primitives_get`

---

## `GET` /api/exploit-cat/memory-primitives/cves

- **Endpoint:** `api_exploit_cat_memory_primitives_cves`

---

## `GET` /api/exploit-cat/memory-primitives/describe

- **Endpoint:** `api_exploit_cat_memory_primitives_describe`

---

## `GET` /api/exploit-cat/memory-primitives/list

- **Endpoint:** `api_exploit_cat_memory_primitives_list`

---

## `POST` /api/exploit-cat/memory-primitives/map-to-exploit

- **Endpoint:** `api_exploit_cat_memory_primitives_map_to_exploit`

---

## `GET` /api/exploit-cat/memory-primitives/mitigations/<name>

- **Endpoint:** `api_exploit_cat_memory_primitives_mitigations`

---

## `POST` /api/exploit-cat/memory-primitives/simulate

- **Endpoint:** `api_exploit_cat_memory_primitives_simulate`

---

## `GET` /api/exploit-cat/messaging-rce/cves

- **Endpoint:** `api_messaging_rce_cves`

---

## `GET` /api/exploit-cat/messaging-rce/describe

- **Endpoint:** `api_messaging_rce_describe`

---

## `POST` /api/exploit-cat/messaging-rce/generate-payload

- **Endpoint:** `api_messaging_rce_generate_payload`

---

## `GET` /api/exploit-cat/messaging-rce/primitives

- **Endpoint:** `api_messaging_rce_primitives`

---

## `POST` /api/exploit-cat/messaging-rce/simulate-imessage

- **Endpoint:** `api_messaging_rce_simulate_imessage`

---

## `POST` /api/exploit-cat/messaging-rce/simulate-signal

- **Endpoint:** `api_messaging_rce_simulate_signal`

---

## `POST` /api/exploit-cat/messaging-rce/simulate-telegram

- **Endpoint:** `api_messaging_rce_simulate_telegram`

---

## `POST` /api/exploit-cat/messaging-rce/simulate-whatsapp

- **Endpoint:** `api_messaging_rce_simulate_whatsapp`

---

## `POST` /api/exploit-cat/ssrf-exploit/blind-ssrf

- **Endpoint:** `api_ssrf_exploit_blind_ssrf`

---

## `POST` /api/exploit-cat/ssrf-exploit/cloud-metadata

- **Endpoint:** `api_ssrf_exploit_cloud_metadata`

---

## `GET` /api/exploit-cat/ssrf-exploit/cves

- **Endpoint:** `api_ssrf_exploit_cves`

---

## `GET` /api/exploit-cat/ssrf-exploit/describe

- **Endpoint:** `api_ssrf_exploit_describe`

---

## `POST` /api/exploit-cat/ssrf-exploit/dns-rebinding

- **Endpoint:** `api_ssrf_exploit_dns_rebinding`

---

## `POST` /api/exploit-cat/ssrf-exploit/generate-payload

- **Endpoint:** `api_ssrf_exploit_generate_payload`

---

## `GET` /api/exploit-cat/ssrf-exploit/primitives

- **Endpoint:** `api_ssrf_exploit_primitives`

---

## `POST` /api/exploit-cat/ssrf-exploit/simulate

- **Endpoint:** `api_ssrf_exploit_simulate`

---

## `GET` /api/exploits/chains

- **Endpoint:** `api_exploits_chains`

---

## `GET` /api/exploits/cve/search

- **Endpoint:** `api_exploits_cve_search`

---

## `GET` /api/exploits/db

- **Endpoint:** `api_exploits_db`

---

## `POST` /api/exploits/poc

- **Endpoint:** `api_exploits_poc`

---

## `GET` /api/external-providers

Return external provider list.

- **Endpoint:** `api_external_providers`

---

## `GET` /api/files/list

- **Endpoint:** `api_files_list`

---

## `GET` /api/files/read

- **Endpoint:** `api_files_read`

---

## `POST` /api/files/upload

- **Endpoint:** `api_files_upload`

---

## `POST` /api/fingerprint/compare

- **Endpoint:** `api_fingerprint_compare`

---

## `GET` /api/fingerprint/detect

- **Endpoint:** `api_fingerprint_detect`

---

## `GET` /api/fingerprint/tips

- **Endpoint:** `api_fingerprint_tips`

---

## `GET` /api/gateway

- **Endpoint:** `api_gateway_get`

---

## `GET, POST` /api/gateway/messages

- **Endpoint:** `api_gateway_messages`

---

## `GET` /api/gateway/platforms

- **Endpoint:** `api_gateway_platforms`

---

## `POST` /api/gateway/platforms/<name>/connect

- **Endpoint:** `api_gateway_connect`

---

## `POST` /api/gateway/platforms/<name>/disconnect

- **Endpoint:** `api_gateway_disconnect`

---

## `GET` /api/gateway/stats

- **Endpoint:** `api_gateway_stats`

---

## `POST` /api/gateway/transfer

- **Endpoint:** `api_gateway_transfer`

---

## `POST` /api/gateway/voice/transcribe

- **Endpoint:** `api_gateway_voice_transcribe`

---

## `GET` /api/godmode

- **Endpoint:** `api_godmode_state`

---

## `POST` /api/godmode/campaign

- **Endpoint:** `api_godmode_campaign`

---

## `POST` /api/godmode/copy-skill

- **Endpoint:** `api_godmode_copy_skill`

---

## `POST` /api/godmode/disable

- **Endpoint:** `api_godmode_disable`

---

## `POST` /api/godmode/enable

- **Endpoint:** `api_godmode_enable`

---

## `GET` /api/godmode/fallback-chain

- **Endpoint:** `api_godmode_fallback_chain`

---

## `POST` /api/godmode/toggle

- **Endpoint:** `api_godmode_toggle`

---

## `GET` /api/gpu

GPU telemetry endpoint — returns flat state (backward compat) plus

- **Endpoint:** `api_gpu`

---

## `GET` /api/gpu-workstation

Return GPU workstation telemetry.

- **Endpoint:** `api_gpu_workstation`

---

## `GET` /api/gpu-workstation/loss

Return training loss curve data.

- **Endpoint:** `api_gpu_workstation_loss`

---

## `GET` /api/gpu/metrics

Return GPU performance metrics (utilization, memory, temperature).

- **Endpoint:** `api_gpu_metrics`

---

## `POST` /api/gpu/perf/disable

Disable GPU optimizations.

- **Endpoint:** `api_gpu_perf_disable`

---

## `POST` /api/gpu/perf/enable

Enable GPU optimizations (CUDA graphs, quantized KV).

- **Endpoint:** `api_gpu_perf_enable`

---

## `GET` /api/gpu/perf/recommend

Get GPU optimization recommendations based on hardware.

- **Endpoint:** `api_gpu_perf_recommend`

---

## `GET` /api/gpu/perf/status

Check which GPU optimizations are active.

- **Endpoint:** `api_gpu_perf_status`

---

## `POST` /api/gpu/scan

- **Endpoint:** `api_gpu_scan`

---

## `GET` /api/gpu/warmup

- **Endpoint:** `api_gpu_warmup_status`

---

## `POST` /api/gpu/warmup

- **Endpoint:** `api_gpu_warmup_run`

---

## `GET` /api/gpu/warmup/config

- **Endpoint:** `api_gpu_warmup_config`

---

## `GET` /api/gpu/warmup/detect

- **Endpoint:** `api_gpu_warmup_detect`

---

## `GET` /api/gpu/warmup/results

- **Endpoint:** `api_gpu_warmup_results`

---

## `GET` /api/health

- **Endpoint:** `health`

---

## `GET` /api/health/alerts

Return current alerts from alerts.json.

- **Endpoint:** `api_health_alerts`

---

## `GET` /api/health/full

Return cached full health data (GPU, disk, memory, deps, alerts).

- **Endpoint:** `api_health_full`

---

## `POST` /api/health/trigger

Manually trigger a health check.

- **Endpoint:** `api_health_trigger`

---

## `GET` /api/hermes-status

- **Endpoint:** `api_hermes_status`

---

## `PUT, GET, DELETE, POST` /api/hermes/proxy/<path:subpath>

- **Endpoint:** `api_hermes_proxy`

---

## `GET` /api/hot-models

- **Endpoint:** `api_hot_models`

---

## `GET` /api/i18n/locales

- **Endpoint:** `api_i18n_locales`

---

## `POST` /api/i18n/set

- **Endpoint:** `api_i18n_set`

---

## `GET` /api/i18n/strings/<locale>

- **Endpoint:** `api_i18n_strings`

---

## `POST` /api/identity/monitor

- **Endpoint:** `api_identity_monitor`

---

## `PUT` /api/identity/roles

- **Endpoint:** `api_identity_roles`

---

## `GET` /api/identity/sessions

- **Endpoint:** `api_identity_sessions`

---

## `GET` /api/identity/users

- **Endpoint:** `api_identity_users`

---

## `PUT` /api/incidents/<incident_id>/status

- **Endpoint:** `api_incidents_update_status`

---

## `POST` /api/incidents/create

- **Endpoint:** `api_incidents_create`

---

## `GET` /api/incidents/list

- **Endpoint:** `api_incidents_list`

---

## `GET` /api/incidents/playbooks

- **Endpoint:** `api_incidents_playbooks`

---

## `GET` /api/ios-exploit/cves

- **Endpoint:** `api_ios_exploit_cves`

---

## `GET` /api/ios-exploit/describe

- **Endpoint:** `api_ios_exploit_describe`

---

## `POST` /api/ios-exploit/image

- **Endpoint:** `api_ios_exploit_image`

---

## `POST` /api/ios-exploit/imessage

- **Endpoint:** `api_ios_exploit_imessage`

---

## `POST` /api/ios-exploit/kernel

- **Endpoint:** `api_ios_exploit_kernel`

---

## `POST` /api/ios-exploit/webkit

- **Endpoint:** `api_ios_exploit_webkit`

---

## `GET` /api/iot-exploit/cves

- **Endpoint:** `api_iot_exploit_cves`

---

## `POST` /api/iot-exploit/default-creds

- **Endpoint:** `api_iot_exploit_default_creds`

---

## `GET` /api/iot-exploit/describe

- **Endpoint:** `api_iot_exploit_describe`

---

## `POST` /api/iot-exploit/firmware

- **Endpoint:** `api_iot_exploit_firmware`

---

## `POST` /api/iot-exploit/hardware-debug

- **Endpoint:** `api_iot_exploit_hardware_debug`

---

## `POST` /api/iot-exploit/mqtt

- **Endpoint:** `api_iot_exploit_mqtt`

---

## `GET` /api/iot-scan/devices

- **Endpoint:** `api_iot_scan_devices`

---

## `POST` /api/iot-scan/start

- **Endpoint:** `api_iot_scan_start`

---

## `POST` /api/iot/assess

- **Endpoint:** `api_iot_assess`

---

## `GET` /api/iot/firmware

- **Endpoint:** `api_iot_firmware`

---

## `GET` /api/jobs

Return all scheduled jobs.

- **Endpoint:** `api_jobs_list`

---

## `DELETE` /api/jobs/<id>/delete

Delete a job.

- **Endpoint:** `api_job_delete`

---

## `POST` /api/jobs/<id>/run

Run a job immediately.

- **Endpoint:** `api_job_run`

---

## `POST` /api/jobs/<id>/toggle

Toggle a job enabled/disabled.

- **Endpoint:** `api_job_toggle`

---

## `POST` /api/jobs/create

Create a new job.

- **Endpoint:** `api_job_create`

---

## `GET` /api/linux-exploit/cves

- **Endpoint:** `api_linux_exploit_cves`

---

## `GET` /api/linux-exploit/describe

- **Endpoint:** `api_linux_exploit_describe`

---

## `POST` /api/linux-exploit/dirty-pipe

- **Endpoint:** `api_linux_exploit_dirty_pipe`

---

## `POST` /api/linux-exploit/docker-escape

- **Endpoint:** `api_linux_exploit_docker_escape`

---

## `POST` /api/linux-exploit/glibc-heap

- **Endpoint:** `api_linux_exploit_glibc_heap`

---

## `POST` /api/linux-exploit/systemd

- **Endpoint:** `api_linux_exploit_systemd`

---

## `GET` /api/logs

- **Endpoint:** `api_logs`

---

## `POST` /api/logs/clear

- **Endpoint:** `api_logs_clear`

---

## `GET` /api/logs/loki/label/<name>/values

- **Endpoint:** `api_logs_loki_label_values`

---

## `GET` /api/logs/loki/labels

- **Endpoint:** `api_logs_loki_labels`

---

## `GET` /api/logs/loki/query

- **Endpoint:** `api_logs_loki_query`

---

## `GET` /api/loot

- **Endpoint:** `api_loot_get`

---

## `DELETE` /api/loot/<category>/<idx>

- **Endpoint:** `api_loot_delete`

---

## `POST` /api/loot/clear

- **Endpoint:** `api_loot_clear`

---

## `GET` /api/macos-exploit/cves

- **Endpoint:** `api_macos_exploit_cves`

---

## `GET` /api/macos-exploit/describe

- **Endpoint:** `api_macos_exploit_describe`

---

## `POST` /api/macos-exploit/image

- **Endpoint:** `api_macos_exploit_image`

---

## `POST` /api/macos-exploit/kernel

- **Endpoint:** `api_macos_exploit_kernel`

---

## `POST` /api/macos-exploit/metal

- **Endpoint:** `api_macos_exploit_metal`

---

## `POST` /api/macos-exploit/safari

- **Endpoint:** `api_macos_exploit_safari`

---

## `POST` /api/malware/analyze

- **Endpoint:** `api_malware_analyze`

---

## `GET` /api/malware/classes

- **Endpoint:** `api_malware_classes`

---

## `GET` /api/malware/hash/<sample_hash>

- **Endpoint:** `api_malware_hash`

---

## `GET` /api/malware/yara

- **Endpoint:** `api_malware_yara`

---

## `GET` /api/mcp

- **Endpoint:** `api_mcp`

---

## `POST` /api/mcp/register

- **Endpoint:** `api_mcp_register`

---

## `GET` /api/memory

- **Endpoint:** `api_memory_get`

---

## `GET, POST` /api/memory/learnings

- **Endpoint:** `api_memory_learnings`

---

## `GET, POST` /api/memory/preferences

- **Endpoint:** `api_memory_preferences`

---

## `GET, POST` /api/memory/projects

- **Endpoint:** `api_memory_projects`

---

## `DELETE` /api/memory/projects/<name>

- **Endpoint:** `api_memory_delete_project`

---

## `GET` /api/memory/stats

- **Endpoint:** `api_memory_stats`

---

## `GET` /api/metrics

- **Endpoint:** `api_metrics`

---

## `GET` /api/metrics/runtime

Aggregated runtime stats from all logging sources.

- **Endpoint:** `api_metrics_runtime`

---

## `GET` /api/monitor/alerts

- **Endpoint:** `api_monitor_alerts`

---

## `GET` /api/monitor/anomalies

- **Endpoint:** `api_monitor_anomalies`

---

## `POST` /api/monitor/configure

- **Endpoint:** `api_monitor_configure`

---

## `GET` /api/monitor/metrics

- **Endpoint:** `api_monitor_metrics`

---

## `POST` /api/net-scan/start

- **Endpoint:** `api_net_scan_start`

---

## `GET` /api/net-scan/status

- **Endpoint:** `api_net_scan_status`

---

## `POST` /api/network/optimize

- **Endpoint:** `api_network_optimize`

---

## `GET` /api/network/quality

- **Endpoint:** `api_network_quality`

---

## `GET` /api/network/status

- **Endpoint:** `api_network_status`

---

## `POST` /api/network/tor/circuit

- **Endpoint:** `api_network_tor_circuit`

---

## `POST` /api/network/vpn/toggle

- **Endpoint:** `api_network_vpn_toggle`

---

## `GET` /api/nfc-exploit/cves

- **Endpoint:** `api_nfc_exploit_cves`

---

## `GET` /api/nfc-exploit/describe

- **Endpoint:** `api_nfc_exploit_describe`

---

## `POST` /api/nfc-exploit/emv-clone

- **Endpoint:** `api_nfc_exploit_emv_clone`

---

## `POST` /api/nfc-exploit/ndef-inject

- **Endpoint:** `api_nfc_exploit_ndef_inject`

---

## `POST` /api/nfc-exploit/payment-intercept

- **Endpoint:** `api_nfc_exploit_payment_intercept`

---

## `POST` /api/nfc-exploit/relay

- **Endpoint:** `api_nfc_exploit_relay`

---

## `POST` /api/nfc-exploit/rfid-skim

- **Endpoint:** `api_nfc_exploit_rfid_skim`

---

## `GET` /api/notifications

- **Endpoint:** `api_notifications`

---

## `POST` /api/notifications/clear

- **Endpoint:** `api_notifications_clear`

---

## `GET, POST` /api/notifications/settings

- **Endpoint:** `api_notifications_settings`

---

## `GET` /api/permissions

- **Endpoint:** `api_permissions`

---

## `POST` /api/permissions/check

- **Endpoint:** `api_permissions_check`

---

## `GET` /api/permissions/list

Return all agent permissions.

- **Endpoint:** `api_permissions_list`

---

## `POST` /api/permissions/set

Set a permission toggle.

- **Endpoint:** `api_permissions_set`

---

## `GET, POST` /api/presets

- **Endpoint:** `api_presets`

---

## `DELETE` /api/presets/<path:name>

- **Endpoint:** `api_delete_preset`

---

## `POST` /api/presets/<path:name>/apply

- **Endpoint:** `api_apply_preset`

---

## `GET` /api/prompts

- **Endpoint:** `api_get_prompts`

---

## `POST` /api/prompts

- **Endpoint:** `api_create_prompt`

---

## `PUT` /api/prompts/<int:prompt_id>

- **Endpoint:** `api_update_prompt`

---

## `DELETE` /api/prompts/<int:prompt_id>

- **Endpoint:** `api_delete_prompt`

---

## `GET` /api/providers

- **Endpoint:** `api_providers`

---

## `POST` /api/proxy-chain/configure

- **Endpoint:** `api_proxy_chain_configure`

---

## `GET` /api/proxy-chain/health

- **Endpoint:** `api_proxy_chain_health`

---

## `GET, POST` /api/proxy-chain/rotate

- **Endpoint:** `api_proxy_chain_rotate`

---

## `GET` /api/proxy-chain/status

- **Endpoint:** `api_proxy_chain_status`

---

## `POST` /api/rbac/check

- **Endpoint:** `rbac.check`

---

## `GET` /api/rbac/godmode

- **Endpoint:** `rbac.godmode_status`

---

## `POST` /api/rbac/godmode/campaign

- **Endpoint:** `rbac.godmode_campaign`

---

## `GET` /api/rbac/godmode/disable

- **Endpoint:** `rbac.godmode_disable`

---

## `GET` /api/rbac/godmode/enable

- **Endpoint:** `rbac.godmode_enable`

---

## `POST` /api/rbac/godmode/toggle

- **Endpoint:** `rbac.godmode_toggle`

---

## `GET` /api/rbac/permissions

- **Endpoint:** `rbac.get_permissions`

---

## `PUT` /api/rbac/permissions

- **Endpoint:** `rbac.set_permissions`

---

## `GET` /api/rbac/roles

- **Endpoint:** `rbac.list_roles`

---

## `GET` /api/rbac/users

- **Endpoint:** `rbac.list_users`

---

## `POST` /api/rbac/users

- **Endpoint:** `rbac.add_user`

---

## `DELETE` /api/rbac/users/<username>

- **Endpoint:** `rbac.delete_user`

---

## `GET, POST` /api/remote-access/ssh/keys

- **Endpoint:** `api_remote_access_ssh_keys`

---

## `POST` /api/remote-access/ssh/start

- **Endpoint:** `api_remote_access_ssh_start`

---

## `POST` /api/remote-access/ssh/stop

- **Endpoint:** `api_remote_access_ssh_stop`

---

## `GET` /api/remote-access/status

- **Endpoint:** `api_remote_access_status`

---

## `POST` /api/remote-access/vnc/password

- **Endpoint:** `api_remote_access_vnc_password`

---

## `POST` /api/remote-access/vnc/start

- **Endpoint:** `api_remote_access_vnc_start`

---

## `POST` /api/remote-access/vnc/stop

- **Endpoint:** `api_remote_access_vnc_stop`

---

## `GET` /api/salad

- **Endpoint:** `api_salad`

---

## `GET` /api/salad/config

- **Endpoint:** `api_salad_config_get`

---

## `POST` /api/salad/config

- **Endpoint:** `api_salad_config_post`

---

## `GET` /api/salad/gpu

- **Endpoint:** `api_salad_gpu`

---

## `GET` /api/salad/history

- **Endpoint:** `api_salad_history`

---

## `GET` /api/sandbox

- **Endpoint:** `api_sandbox`

---

## `GET` /api/sandbox/devices

Return list of C2-connected devices.

- **Endpoint:** `api_sandbox_devices`

---

## `POST` /api/sandbox/devices/<device_id>/action

Execute action on C2 device.

- **Endpoint:** `api_sandbox_device_action`

---

## `GET` /api/sandbox/resources

Return system resource usage.

- **Endpoint:** `api_sandbox_resources`

---

## `POST` /api/sandbox/run

- **Endpoint:** `api_sandbox_run`

---

## `GET` /api/sandbox/tools

Return list of available security tools.

- **Endpoint:** `api_sandbox_tools`

---

## `GET` /api/sandbox/vms

Return list of VMs in the sandbox.

- **Endpoint:** `api_sandbox_vms`

---

## `GET` /api/sandbox/vms/<vm_id>/console

Get VM console access URL.

- **Endpoint:** `api_sandbox_vm_console`

---

## `POST` /api/sandbox/vms/<vm_id>/power

Power on/off/restart a VM.

- **Endpoint:** `api_sandbox_vm_power`

---

## `GET` /api/scheduler

- **Endpoint:** `api_scheduler`

---

## `GET` /api/scheduler/jobs

- **Endpoint:** `api_scheduler_jobs`

---

## `POST` /api/scheduler/jobs

- **Endpoint:** `api_scheduler_create_job`

---

## `DELETE` /api/scheduler/jobs/<job_id>

- **Endpoint:** `api_scheduler_delete_job`

---

## `POST` /api/scheduler/jobs/<job_id>/toggle

- **Endpoint:** `api_scheduler_toggle`

---

## `GET` /api/secrets

- **Endpoint:** `api_secrets_list`

---

## `POST` /api/secrets

- **Endpoint:** `api_secrets_store`

---

## `GET` /api/secrets/<name>

- **Endpoint:** `api_secrets_get`

---

## `DELETE` /api/secrets/<name>

- **Endpoint:** `api_secrets_delete`

---

## `POST` /api/secrets/<name>/rotate

- **Endpoint:** `api_secrets_rotate`

---

## `GET` /api/secrets/export

- **Endpoint:** `api_secrets_export`

---

## `POST` /api/secrets/import

- **Endpoint:** `api_secrets_import`

---

## `GET` /api/services

- **Endpoint:** `api_services`

---

## `GET, POST` /api/settings

- **Endpoint:** `api_settings`

---

## `GET` /api/shodan/health

- **Endpoint:** `api_shodan_health`

---

## `GET` /api/shodan/host/<ip>

- **Endpoint:** `api_shodan_host`

---

## `GET` /api/shodan/key

- **Endpoint:** `api_shodan_key_status`

---

## `PUT` /api/shodan/key

- **Endpoint:** `api_shodan_key_save`

---

## `POST` /api/shodan/search

- **Endpoint:** `api_shodan_search`

---

## `GET` /api/skills

- **Endpoint:** `api_skills`

---

## `GET` /api/skills/activity

- **Endpoint:** `api_activity`

---

## `GET` /api/skills/aggregated

- **Endpoint:** `api_skills_aggregated`

---

## `GET` /api/skills/available

- **Endpoint:** `api_skills_available`

---

## `GET` /api/skills/catalog

- **Endpoint:** `api_skills_catalog`

---

## `POST` /api/skills/catalog/install

- **Endpoint:** `api_skills_catalog_install`

---

## `POST` /api/skills/catalog/refresh

- **Endpoint:** `api_skills_catalog_refresh`

---

## `DELETE` /api/skills/delete/<name>

- **Endpoint:** `api_delete_skill`

---

## `POST` /api/skills/log

- **Endpoint:** `api_log_activity`

---

## `POST` /api/skills/save

- **Endpoint:** `api_save_skill`

---

## `POST` /api/skills/scan

Scan activity log and auto-create skills.

- **Endpoint:** `api_scan_skills`

---

## `POST` /api/social-eng/generate

- **Endpoint:** `api_social_eng_generate`

---

## `GET` /api/social-eng/quiz

- **Endpoint:** `api_social_eng_quiz`

---

## `GET` /api/social-eng/templates

- **Endpoint:** `api_social_eng_templates`

---

## `GET` /api/stats

- **Endpoint:** `stats`

---

## `GET` /api/status

- **Endpoint:** `api_status`

---

## `GET` /api/subagents

- **Endpoint:** `api_subagents`

---

## `POST` /api/subagents

- **Endpoint:** `api_create_subagent`

---

## `DELETE` /api/subagents/<sa_id>

- **Endpoint:** `api_delete_subagent`

---

## `GET` /api/subagents/<sa_id>/log

- **Endpoint:** `api_subagent_log`

---

## `POST` /api/subagents/<sa_id>/pause

- **Endpoint:** `api_pause_subagent`

---

## `POST` /api/subagents/<sa_id>/resume

- **Endpoint:** `api_resume_subagent`

---

## `GET` /api/system

Return system resource usage.

- **Endpoint:** `api_system`

---

## `GET` /api/threat-intel/actors

- **Endpoint:** `api_threat_intel_actors`

---

## `GET` /api/threat-intel/feeds

- **Endpoint:** `api_threat_intel_feeds`

---

## `GET` /api/threat-intel/iocs

- **Endpoint:** `api_threat_intel_iocs`

---

## `POST` /api/threat-intel/refresh

- **Endpoint:** `api_threat_intel_refresh`

---

## `GET` /api/todos

List all todos for the current user with pagination and filters.

- **Endpoint:** `todos.list_todos`

---

## `POST` /api/todos

Create a new todo.

- **Endpoint:** `todos.create_todo`

---

## `GET` /api/todos/<int:todo_id>

Get a single todo by ID.

- **Endpoint:** `todos.get_todo`

---

## `PUT` /api/todos/<int:todo_id>

Update an existing todo.

- **Endpoint:** `todos.update_todo`

---

## `DELETE` /api/todos/<int:todo_id>

Delete a todo.

- **Endpoint:** `todos.delete_todo`

---

## `PATCH` /api/todos/<int:todo_id>/toggle

Toggle the completed status of a todo.

- **Endpoint:** `todos.toggle_todo`

---

## `GET` /api/training

- **Endpoint:** `api_training_status`

---

## `POST` /api/training/abliterate

- **Endpoint:** `api_abliterate`

---

## `GET` /api/training/datasets

- **Endpoint:** `api_datasets`

---

## `POST` /api/training/datasets

- **Endpoint:** `api_upload_dataset`

---

## `GET` /api/training/datasets

- **Endpoint:** `api_training_datasets_list`

---

## `POST` /api/training/datasets

- **Endpoint:** `api_training_dataset_create`

---

## `DELETE` /api/training/datasets/<ds_id>

- **Endpoint:** `api_delete_dataset`

---

## `POST` /api/training/deploy

- **Endpoint:** `api_training_deploy`

---

## `GET` /api/training/gpu-status

- **Endpoint:** `api_training_gpu_status`

---

## `POST` /api/training/jobs

- **Endpoint:** `api_create_job`

---

## `GET` /api/training/jobs

- **Endpoint:** `api_training_jobs_list`

---

## `GET` /api/training/jobs/<job_id>

- **Endpoint:** `api_training_job_detail`

---

## `PUT` /api/training/jobs/<job_id>/status

- **Endpoint:** `api_training_job_status`

---

## `GET` /api/training/models

- **Endpoint:** `api_models`

---

## `GET` /api/training/models

- **Endpoint:** `api_training_models_list`

---

## `DELETE` /api/training/models/<mid>

- **Endpoint:** `api_delete_model`

---

## `POST` /api/training/models/<mid>/deploy

- **Endpoint:** `api_deploy_model`

---

## `POST` /api/upload

- **Endpoint:** `api_upload`

---

## `GET` /api/uploads

- **Endpoint:** `api_uploads`

---

## `GET` /api/vuln-scan/results

- **Endpoint:** `api_vuln_scan_results`

---

## `POST` /api/vuln-scan/schedule

- **Endpoint:** `api_vuln_scan_schedule`

---

## `POST` /api/vuln-scan/start

- **Endpoint:** `api_vuln_scan_start`

---

## `GET` /api/vuln-scan/status

- **Endpoint:** `api_vuln_scan_status`

---

## `POST` /api/wifi-scan/start

- **Endpoint:** `api_wifi_scan_start`

---

## `GET` /api/wifi-scan/status

- **Endpoint:** `api_wifi_scan_status`

---

## `GET` /api/wiki/blog

- **Endpoint:** `api_wiki_blog`

---

## `GET` /api/wiki/content/<page>

- **Endpoint:** `api_wiki_content`

---

## `GET` /api/wiki/forum

- **Endpoint:** `api_wiki_forum`

---

## `GET` /api/windows-exploit/cves

- **Endpoint:** `api_windows_exploit_cves`

---

## `GET` /api/windows-exploit/describe

- **Endpoint:** `api_windows_exploit_describe`

---

## `POST` /api/windows-exploit/doc

- **Endpoint:** `api_windows_exploit_doc`

---

## `POST` /api/windows-exploit/eternalblue

- **Endpoint:** `api_windows_exploit_eternalblue`

---

## `POST` /api/windows-exploit/exchange

- **Endpoint:** `api_windows_exploit_exchange`

---

## `POST` /api/windows-exploit/kernel-chain

- **Endpoint:** `api_windows_exploit_kernel_chain`

---

## `POST` /api/windows-exploit/printnightmare

- **Endpoint:** `api_windows_exploit_printnightmare`

---

## `POST` /api/wireless/analyze

- **Endpoint:** `api_wireless_analyze`

---

## `POST` /api/wireless/evil-twin

- **Endpoint:** `api_wireless_evil_twin`

---

## `GET` /api/wireless/handshakes

- **Endpoint:** `api_wireless_handshakes`

---

## `GET` /api/workflow

- **Endpoint:** `api_workflow`

---

## `GET` /api/workflow-designer/templates

- **Endpoint:** `api_workflow_designer_templates`

---

## `POST` /api/workflow-designer/templates

- **Endpoint:** `api_workflow_designer_templates_save`

---

## `DELETE` /api/workflow-designer/templates/<template_id>

- **Endpoint:** `api_workflow_designer_templates_delete`

---

## `GET` /api/workflow-designer/workflows

- **Endpoint:** `api_workflow_designer_workflows_list`

---

## `POST` /api/workflow-designer/workflows

- **Endpoint:** `api_workflow_designer_workflows_save`

---

## `GET` /api/workflow-designer/workflows/<name>

- **Endpoint:** `api_workflow_designer_workflows_get`

---

## `DELETE` /api/workflow-designer/workflows/<name>

- **Endpoint:** `api_workflow_designer_workflows_delete`

---

## `DELETE` /api/workflow/delete/<name>

- **Endpoint:** `api_workflow_delete`

---

## `GET` /api/workflow/registries

- **Endpoint:** `api_workflow_registries`

---

## `POST` /api/workflow/save

- **Endpoint:** `api_workflow_save`

---

## `GET` /apt-intelligence

- **Endpoint:** `page_apt_intelligence`

---

## `POST` /army/close-all

- **Endpoint:** `army_close_all`

---

## `GET` /audit

- **Endpoint:** `audit_page`

---

## `GET` /auth/login

- **Endpoint:** `auth_login_page`

---

## `POST` /auth/login

- **Endpoint:** `auth_login`

---

## `POST` /auth/logout

- **Endpoint:** `auth_logout`

---

## `GET` /auth/me

- **Endpoint:** `auth_me`

---

## `POST` /auth/refresh

- **Endpoint:** `auth_refresh`

---

## `GET` /auth/users

- **Endpoint:** `auth_list_users`

---

## `POST` /auth/users

- **Endpoint:** `auth_create_user`

---

## `DELETE` /auth/users/<username>

- **Endpoint:** `auth_delete_user`

---

## `GET` /automations

- **Endpoint:** `automations_page`

---

## `GET` /blog

- **Endpoint:** `blog_page`

---

## `GET` /browser-v2

- **Endpoint:** `browser_v2_page`

---

## `GET` /c2

- **Endpoint:** `c2_page`

---

## `GET` /campaign-manager

- **Endpoint:** `campaign_manager_page`

---

## `GET` /campaign-settings

- **Endpoint:** `campaign_settings_page`

---

## `GET` /cloud-exploitation

- **Endpoint:** `page_cloud_exploitation`

---

## `GET` /communications

- **Endpoint:** `communications_page`

---

## `GET` /config

- **Endpoint:** `config_page`

---

## `GET` /dashboard

- **Endpoint:** `dashboard`

---

## `GET` /dashboard

- **Endpoint:** `dashboard_page`

---

## `GET` /ddns-manager

- **Endpoint:** `ddns_manager_page`

---

## `GET` /dependency-agent

- **Endpoint:** `dependency_agent_page`

---

## `GET` /desktop

- **Endpoint:** `desktop_page`

---

## `GET` /device-fingerprint

- **Endpoint:** `page_device_fingerprint`

---

## `GET` /encryption

- **Endpoint:** `encryption_page`

---

## `GET` /errors

- **Endpoint:** `errors_page`

---

## `GET` /extensions

- **Endpoint:** `extensions_page`

---

## `GET` /external-providers

- **Endpoint:** `external_providers_page`

---

## `GET` /files

- **Endpoint:** `files_page`

---

## `GET` /forum

- **Endpoint:** `forum_page`

---

## `GET` /gateway

- **Endpoint:** `gateway_page`

---

## `GET` /godmode

- **Endpoint:** `godmode_page`

---

## `GET` /gpu

- **Endpoint:** `gpu_page`

---

## `GET` /gpu-warmup

- **Endpoint:** `gpu_warmup_page`

---

## `GET` /gpu-workstation

- **Endpoint:** `gpu_workstation_page`

---

## `GET` /health

- **Endpoint:** `health_page`

---

## `GET` /hermes

- **Endpoint:** `hermes_page`

---

## `GET` /identity-mgmt

- **Endpoint:** `identity_mgmt_page`

---

## `GET` /incident-response

- **Endpoint:** `page_incident_response`

---

## `GET` /iot-exploitation

- **Endpoint:** `page_iot_exploitation`

---

## `GET` /jobs

- **Endpoint:** `jobs_page`

---

## `GET` /logs

- **Endpoint:** `logs_page`

---

## `GET` /logs-stream

- **Endpoint:** `logs_stream_page`

---

## `GET` /loot

- **Endpoint:** `loot_page`

---

## `GET` /malware-analysis

- **Endpoint:** `page_malware_analysis`

---

## `GET` /mcp

- **Endpoint:** `mcp_page`

---

## `GET` /memory

- **Endpoint:** `memory_page`

---

## `GET` /metrics

- **Endpoint:** `metrics_page`

---

## `GET` /model-registry

- **Endpoint:** `model_registry_page`

---

## `GET` /network

- **Endpoint:** `network_page`

---

## `GET` /network-auto

- **Endpoint:** `network_auto_page`

---

## `GET` /network-exploitation

- **Endpoint:** `page_network_exploitation`

---

## `GET` /permissions

- **Endpoint:** `permissions_page`

---

## `GET` /plugins-manage

- **Endpoint:** `plugins_manage_page`

---

## `GET` /predictive-analytics

- **Endpoint:** `page_predictive_analytics`

---

## `GET` /prompts

- **Endpoint:** `prompts_page`

---

## `GET` /providers

- **Endpoint:** `providers_page`

---

## `GET` /proxy-chain

- **Endpoint:** `proxy_chain_page`

---

## `GET` /rbac

- **Endpoint:** `rbac_page`

---

## `GET` /realtime-monitor

- **Endpoint:** `realtime_monitor_page`

---

## `GET` /remote-access

- **Endpoint:** `remote_access_page`

---

## `GET` /salad

- **Endpoint:** `salad_page`

---

## `GET` /sandbox

- **Endpoint:** `page_sandbox`

---

## `GET` /scheduler

- **Endpoint:** `scheduler_page`

---

## `GET` /sdlc

- **Endpoint:** `sdlc_page`

---

## `GET` /secrets

- **Endpoint:** `secrets_page`

---

## `GET` /security

- **Endpoint:** `security_page`

---

## `GET` /shodan

- **Endpoint:** `shodan_page`

---

## `GET` /skills

- **Endpoint:** `skills_page`

---

## `GET` /skills-catalog

- **Endpoint:** `skills_catalog_page`

---

## `GET` /social-engineering

- **Endpoint:** `page_social_engineering`

---

## `GET` /subagents

- **Endpoint:** `subagents_page`

---

## `GET` /terminal

- **Endpoint:** `terminal_page`

---

## `GET` /threat-intel

- **Endpoint:** `threat_intel_page`

---

## `GET` /todos

- **Endpoint:** `todos_page`

---

## `GET` /training

- **Endpoint:** `training_page`

---

## `GET` /vuln-scanner

- **Endpoint:** `vuln_scanner_page`

---

## `GET` /wiki-dashboard

- **Endpoint:** `wiki_dashboard_page`

---

## `GET` /wireless-exploitation

- **Endpoint:** `page_wireless_exploitation`

---

## `GET` /workflow-designer

- **Endpoint:** `workflow_designer_page`

---

## `GET` /workflows

- **Endpoint:** `workflows_page`

---

## `GET` /ws-test

- **Endpoint:** `ws_test_page`

---

## `GET` /zero-day

- **Endpoint:** `page_zero_day`

---
