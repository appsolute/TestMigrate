//
//  DetailViewController.swift
//  TestMigrate
//
//  Created by Nattapon Nimakul on 1/26/2559 BE.
//  Copyright © 2559 Aspsolute Soft. All rights reserved.
//

import UIKit

class DetailViewController: UIViewController {

    var _detailItem: NSObject?
    var detailItem: NSObject? {
//        get {
//            return _detailItem
//        }
//        
//        set {
//            if _detailItem != newValue {
//                _detailItem = newValue
//            
//                // Update the view.
//                configureView()
//            }
//        }
        
        didSet {
            if oldValue != detailItem {
                // Update the view.
                configureView()
            }
        }
    }
    @IBOutlet weak var detailDescriptionLabel: UILabel!

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        configureView()
    }

    func configureView() {
        if let detailItemValue = self.detailItem {
            detailDescriptionLabel?.text = detailItemValue.description
        }
    }

}
