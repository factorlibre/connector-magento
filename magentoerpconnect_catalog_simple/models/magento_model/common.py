# -*- coding: utf-8 -*-
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import datetime, timedelta
from openerp import api, models, fields
from openerp.addons.connector.session import ConnectorSession
from ..magento_product.exporter import export_product_batch


class MagentoBackend(models.Model):
    _inherit = 'magento.backend'

    auto_bind_product = fields.Boolean(
        string='Auto Bind Product',
        default=False,
        help="Tic that box if you want to automatically export the"
             "product when it's available for sell (sale_ok is tic)"
    )
    default_mag_tax_id = fields.Many2one('magento.tax.class',
                                         string='Default tax')
    export_products_from_date = fields.Datetime(
        string='Export products from date',
    )

    @api.multi
    def batch_export_products_from_date(self):
        session = ConnectorSession(self.env.cr, self.env.uid,
                                   context=self.env.context)
        export_start_time = datetime.now()
        for backend in self:
            from_date = backend.export_products_from_date
            if from_date:
                from_date = fields.Datetime.from_string(from_date)
            else:
                from_date = None
            export_product_batch.delay(
                session, 'magento.product.product', backend.id,
                from_date)
        next_time = export_start_time - timedelta(seconds=30)
        next_time = fields.Datetime.to_string(next_time)
        self.write({'export_products_from_date': next_time})
