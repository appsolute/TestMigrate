//
//  MasterViewController.h
//  TestMigrate
//
//  Created by Nattapon Nimakul on 1/26/2559 BE.
//  Copyright © 2559 Aspsolute Soft. All rights reserved.
//

#import <UIKit/UIKit.h>

@class DetailViewController;

@interface MasterViewController : UITableViewController

@property (strong, nonatomic) NSMutableArray *objects;
@property (strong, nonatomic) DetailViewController *detailViewController;


@end

