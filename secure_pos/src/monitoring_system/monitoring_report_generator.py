import json
import logging
import threading

from monitoring_system.monitoring_report import MonitoringReport


class MonitoringReportGenerator:

    def __init__(self):
        self.report = MonitoringReport()
        self.labels = None
        self.count_report = 0
        self.lock = threading.RLock()

    def generate_report_json(self):
        report_dict = self.report.to_dict()
        with open("../../data/monitoring_system/report/report" + str(self.count_report) +
                  '.json', 'w', encoding="UTF-8") as json_file:
            json.dump(report_dict, json_file, indent=2)
        logging.info("Generated monitoring report json")

    def count_conflicting_labels(self):
        count_conflicting_labels = 0
        tot_labels = 0
        for row in self.labels.index:
            tot_labels += 1
            expert_label = self.labels["expertValue"][row]
            classifier_label = self.labels["classifierValue"][row]
            if expert_label != classifier_label:
                count_conflicting_labels += 1
        self.report.conflicting_labels = count_conflicting_labels
        self.report.compared_labels = tot_labels

    def count_max_consecutive_conflicting_labels(self):
        max_consecutive_conflicting_labels = 0
        consecutive_conflicting_labels = 0
        consecutive = False
        first = True
        for row in self.labels.index:
            expert_label = self.labels["expertValue"][row]
            classifier_label = self.labels["classifierValue"][row]
            if expert_label != classifier_label:
                if not consecutive:
                    first = True
                    consecutive_conflicting_labels = 0
                if first or consecutive:
                    consecutive_conflicting_labels += 1
                    consecutive = True
                first = False
            else:
                consecutive = False
            if consecutive_conflicting_labels > max_consecutive_conflicting_labels:
                max_consecutive_conflicting_labels = consecutive_conflicting_labels
        self.report.max_consecutive_conflicting_labels = max_consecutive_conflicting_labels

    def generate_report(self, label_df):
        with self.lock:
            self.count_report += 1
            self.labels = label_df

            if self.labels is not None:
                # conto il numero di label discordanti
                self.count_conflicting_labels()

                # conto il numero massimo di label consecutive discordanti
                self.count_max_consecutive_conflicting_labels()

            # genero il file json contente il report
            self.generate_report_json()
