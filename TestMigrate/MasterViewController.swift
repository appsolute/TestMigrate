//
//  MasterViewController.swift
//  TestMigrate
//
//  Created by Nattapon Nimakul on 1/26/2559 BE.
//  Copyright © 2559 Aspsolute Soft. All rights reserved.
//

import UIKit

extension MasterViewController {
    func insertNewObject(sender: NSObject?) {
        if nil == self.objects {
            self.objects = NSMutableArray()
        }
        objects.insertObject(NSDate(), atIndex: 0)
        let indexPath = NSIndexPath(forRow:0, inSection:0)
        self.tableView.insertRowsAtIndexPaths([indexPath], withRowAnimation:.Automatic)
    }
}
