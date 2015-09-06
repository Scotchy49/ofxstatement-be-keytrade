import csv

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine


class KeytradePlugin(Plugin):
    """Sample plugin (for developers only)
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get("charset", "ISO-8859-1"))
        parser = KeytradeParser(f)
        parser.statement.bank_id = "KeytradeBank"
        return parser


class KeytradeParser(CsvStatementParser):

    date_format = "%d.%m.%Y"

    mappings = {
        'check_no': 0,
        'date': 1,
        'payee': 3,
        'memo': 4,
        'amount': 5
    }

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = super(KeytradeParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        reader = csv.reader(self.fin, delimiter=";")
        next(reader, None)
        return reader

    def fix_amount(self, amount):
        return amount.replace('.', '').replace(',', '.')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        transaction_id = line[0]
        date = line[1]
        date_value = line[2]
        account_to = line[3]
        description = line[4]
        line[5] = self.fix_amount(line[5])
        currency = line[6]

        stmtline = super(KeytradeParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'

        return stmtline
