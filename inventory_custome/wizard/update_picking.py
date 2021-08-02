
from odoo import models, fields, api, _

from odoo.exceptions import UserError, ValidationError



class UpdatePicking(models.TransientModel):
     
     _name =  'update.picking'
     _description = 'Update Picking'
   
    
     def action_update_picking(self):
          active_ids = self._context.get('active_ids')
          pikings = self.env['stock.picking'].search([('id', 'in', active_ids)])
          for record in pikings:
               if record.state != 'done':
                    try:
                         for line in record.move_line_ids_without_package:
                              line.qty_done = line.product_uom_qty
                              record.button_validate()
                    except Exception as e:
                         raise UserError(
                         '{} \n Picking Number : {}'.format(e, record.name))
          return {
              'effect': {
                  'fadeout': 'slow',
                  'message': 'Done All Picking',
                  'type': 'rainbow_man'
              }
          }
